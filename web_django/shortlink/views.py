from django.shortcuts import render, redirect, get_object_or_404
from .add_func import generate_random_string
from .models import ShortLinks
import logging
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import redis

# Connecting to REDIS
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Checking the settings from the config.cfg
try:
    url_valid_days  = int(settings.URL_VALID_DAYS)
except ValueError:
    logger.error("The `url-validdays`:`{}` value in the config.cfg is not correct. We use the default value 14.".format(
        settings.URL_VALID_DAYS))
    url_valid_days = 14
try:
    shortlink_length = int(settings.SHORTLINK_LENGTH)
except ValueError:
    logger.error("The `shortlink-length`:`{}` value in the config.cfg is not correct. We use the default value 3."
                 .format(settings.SHORTLINK_LENGTH))
    shortlink_length = 3


logger.info("Valid days of URLs set's to `{}` days. Default Shortlink length:`{}`"
            .format(url_valid_days, shortlink_length))


def mainform(request):

    # If the user is new, we create an entry in the table `django_session` for him using Django methods
    if not ('new_user' in request.session):
        request.session.set_expiry(86400 * url_valid_days)
        request.session['new_user'] = True


    # If the user POST the new URL
    if request.method == 'POST':
        logger.info('POST Request: `{}`'.format(request.POST))

        # The user has POST own shortlink
        if 'shortlink' in request.POST:
            post_shortlink = request.POST['shortlink']
            logger.info('User-shortlink: `{}`'.format(post_shortlink))

            # If the short link already exists
            if ShortLinks.objects.filter(shortlink=post_shortlink).exists():
                logger.info('shortlink: `{}` already exists'.format(post_shortlink))
                return render(request, 'mainform.html',
                              {'usersubparts': ShortLinks.objects.filter(session_key=request.session.session_key),
                               'domain_name': settings.OUT_DOMAIN_NAME,
                               'post_url': request.POST['domain'],
                               'title': settings.MAIN_TITLE,
                               'shortlink' : post_shortlink,
                               'error' : 'The short link `{}` already exists, choose another.'.format(post_shortlink),})
        else:
            # We assign a short link ourselves
            post_shortlink = generate_random_string(shortlink_length)
            logger.info('New-shortlink: `{}`'.format(post_shortlink))
            regeneration_count = 0
            while ShortLinks.objects.filter(shortlink=post_shortlink).exists() and regeneration_count <= 30:
                regeneration_count += 1
                post_shortlink = generate_random_string(shortlink_length)
                logger.warning('Regenerate-New-shortlink: `{}` regeneration_count: {}'.format(post_shortlink,
                                                                                              regeneration_count))

            # if Problems with generating a new short link. inform the user
            if (regeneration_count > 30):
                logger.error('I can not generate a new short link.')
                return render(request, 'mainform.html',
                              {'usersubparts': ShortLinks.objects.filter(session_key=request.session.session_key),
                               'domain_name': settings.OUT_DOMAIN_NAME,
                               'post_url': request.POST['domain'],
                               'title': settings.MAIN_TITLE,
                               'shortlink' : 'I can not generate a short link. ',
                               'error' : 'I can not generate a short link. Contact the resource administrator.',})

        # Everything is fine - we save the results
        post_new_url = ShortLinks(
            session_key = request.session.session_key,
            urls = request.POST['domain'],
            shortlink = post_shortlink,
        )
        post_new_url.save()
        # Save to REDIS
        try:
            r.setex(post_shortlink, url_valid_days * 86400, value=request.POST['domain'])
            logger.info('ShortLink `{}` write to Redis. Value:`{}`'.format(post_shortlink, request.POST['domain']))
        except Exception as e:
            logger.error('Can not connect to REDIS:`{}`'.format(e))

    # Showing the form for the current user according to the session
    logger.info('User request `mainform` from session_key: {}'.format(request.session.session_key))
    return render(request, 'mainform.html',
                      { 'usersubparts' : ShortLinks.objects.filter(session_key=request.session.session_key)
                                            .order_by('-crt_date'),
                        'domain_name': settings.OUT_DOMAIN_NAME,
                        'title' : settings.MAIN_TITLE,})

# Generating a user's link table by his session
def urls_table(request):
    logger.info('User:`{}` Show Page: `{}`'.format(request.session.session_key, request.GET.get('page')))

    # The user uses the search
    if 'find' in request.GET and request.GET.get('find') != "":
        logger.info('User:`{}` Search: `{}`'.format(request.session.session_key, request.GET.get('find')))
        urls_list = ShortLinks.objects \
            .filter(Q(session_key=request.session.session_key),
                    Q(urls__contains=request.GET.get('find')) |
                    Q(shortlink__contains=request.GET.get('find')) ) \
            .order_by('-crt_date')
    else:
        # There is no search: we output all the user's URLs
        urls_list = ShortLinks.objects.filter(session_key=request.session.session_key, ).order_by('-crt_date')

    # Determining how many records to output in the pegenator
    if 'entries' in request.GET:
        logger.info('User:`{}` Change Entriers to `{}`'.format(request.session.session_key, request.GET.get('entries')))
        paginator = Paginator(urls_list, request.GET.get('entries'))
    else:
        paginator = Paginator(urls_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'mainform/urls_table.html', {'page_obj': page_obj, 'domain_name': settings.OUT_DOMAIN_NAME, })

# Redirection by short link
def redirect_to_url(request, short_url):
    # Request to REDIS
    try:
        redirectURL = r.get(short_url)
    except Exception as e:
        logger.error('Can not connect to REDIS:`{}`'.format(e))
        redirectURL = False

    if redirectURL:
        # If the data is in the REDIS
        redirectURL = redirectURL.decode('UTF-8')
        logger.info('ShortLink `{}` in Redis. Value:`{}`'.format(short_url, redirectURL))
    else:
        # Not in REDIS, get from DB
        redirectURL = get_object_or_404(ShortLinks, shortlink=short_url).urls
        # We write in REDIS for the future
        try :
            r.setex(short_url, url_valid_days * 86400, value=redirectURL)
            logger.info('ShortLink `{}` write to Redis. Value:`{}`'.format(short_url, redirectURL))
        except Exception as e:
            logger.error('Can not connect to REDIS:`{}`'.format(e))
    if redirectURL == "{}/{}".format(settings.OUT_DOMAIN_NAME, short_url):
        return render(request, '301.html', status=301)
    else:
        return redirect(redirectURL)

# stub page for error 404
def page_not_found_view(request, exception):
    return render(request, '404.html', status=404)

# stub page for error 500
def server_error(request):
    return render(request, '500.html', status=500)

# stub page for error 301
def many_redirects(request):
    return render(request, '301.html', status=301)