
from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook, static_file
import job
import lookups
import buildd
import package
import packageinstance
import os

def get_app(settings, db, controller):
    app = Bottle()
    app.config={'settings' : settings, 'db' : db, 'controller' : controller}

    local_path = "pybitweb/static"
    installed_path = settings['web']['installed_path']

    def getPath():
        if os.path.exists(local_path):
            return local_path
        elif os.path.exists(installed_path):
            return installed_path
        else:
            return None

    # Helper which abstracts away whether its looking in /usr/share for static assets, as packages, or in a relative direcory i.e. git checkout.
    def getStaticResource(file_path):
        localpath = local_path + file_path
        installedpath = installed_path + file_path
        if os.path.exists(localpath) and os.path.isfile(localpath):
            return localpath
        elif os.path.exists(installedpath) and os.path.isfile(installedpath):
            return installedpath

    @app.error(404)
    def error404(error):
        return 'HTTP Error 404 - Not Found.'

    # Remove this to get more debug.
    #@app.error(500)
    #def error500(error):
    #    return 'HTTP Error 500 - Internal Server Error.'

    # Things in here are applied to all requests. We need to set this header so strict browsers can query it using jquery
    #http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
    @app.hook('after_request')
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

    @app.route('/', method='GET')
    def index():
        return template(getStaticResource("/index.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)
    # favicons
    @app.route('/favicon.ico', method='GET')
    def serve_favicon_ico():
            response.content_type = "image/x-icon"
            return static_file('favicon.ico',root=getPath())

    @app.route('/favicon.png', method='GET')
    def serve_favicon_png():
            response.content_type = "image/png"
            return static_file('favicon.png',root=getPath())

    # static resources like CSS
    @app.route('/bootstrap/<filepath:path>', method='GET')
    def serve_static_res(filepath):
            return static_file(filepath, root=getPath() + "/bootstrap/")

    # Serve javascript resources from local system
    @app.route('/resources/jquery.min.js', method='GET')
    def serve_static_jquery():
            response.content_type = "application/javascript"
            return static_file('jquery.min.js',root='/usr/share/javascript/jquery/')

    @app.route('/resources/jquery.form.min.js', method='GET')
    def serve_static_jquery_forms():
            response.content_type = "application/javascript"
            return static_file('jquery.form.min.js',root='/usr/share/javascript/jquery-form/')

    # static HTML index page
    @app.route('/index.htm', method='GET')
    def serve_static_index():
            return template(getStaticResource("/index.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML index page
    @app.route('/dashboard.htm', method='GET')
    def serve_static_dash():
            return template(getStaticResource("/dashboard.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing arches
    @app.route('/arches.htm', method='GET')
    def serve_static_arches():
            return template(getStaticResource("/arches.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl'])

    # static HTML page listing dists
    @app.route('/dists.htm', method='GET')
    def serve_static_dists():
            return template(getStaticResource("/dists.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl'])

    # static HTML page listing formats
    @app.route('/formats.htm', method='GET')
    def serve_static_formats():
            return template(getStaticResource("/formats.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl'])

    # static HTML page listing statuses
    @app.route('/statuses.htm', method='GET')
    def serve_static_statuses():
            return template(getStaticResource("/statuses.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl'])

    # static HTML page listing suites
    @app.route('/suites.htm', method='GET')
    def serve_static_suites():
            return template(getStaticResource("/suites.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl'])

    # static HTML page listing buildboxes
    @app.route('/buildd.htm', method='GET')
    def serve_static_buildboxes():
            return template(getStaticResource("/buildd.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing jobs
    @app.route('/job.htm', method='GET')
    def serve_static_jobs():
            return template(getStaticResource("/job.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing things
    @app.route('/lookups.htm', method='GET')
    def serve_static_lookups():
            return template(getStaticResource("/lookups.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing packages
    @app.route('/package.htm', method='GET')
    def serve_static_packages():
            return template(getStaticResource("/package.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing package instances
    @app.route('/packageinstance.htm', method='GET')
    def serve_static_package_instances():
            return template(getStaticResource("/packageinstance.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing package instances
    @app.route('/envs.htm', method='GET')
    def serve_static_envs():
            return template(getStaticResource("/envs.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    # static HTML page listing package instances
    @app.route('/blacklist.htm', method='GET')
    def serve_static_blacklist():
            return template(getStaticResource("/blacklist.htm"),
            protocol=settings['web']['protocol'],
            jqueryurl=settings['web']['jqueryurl'],
            jqueryformurl=settings['web']['jqueryformurl']
)

    app.mount('/job', job.get_job_app(settings, db, controller))
    app.mount('/suite', lookups.get_suite_app(settings, db))
    app.mount('/suitearch', lookups.get_suitearch_app(settings, db))
    app.mount('/dist', lookups.get_dist_app(settings, db))
    app.mount('/status',lookups.get_status_app(settings, db))
    app.mount('/arch',lookups.get_arch_app(settings, db))
    app.mount('/format', lookups.get_format_app(settings, db))
    app.mount('/env', lookups.get_env_app(settings, db))
    app.mount('/buildenv_suitearch', lookups.get_buildenv_suitearch_app(settings, db))
    app.mount('/buildd', buildd.get_buildd_app(settings, db, controller))
    app.mount('/package', package.get_packages_app(settings, db, controller))
    app.mount('/packageinstance', packageinstance.get_packageinstance_app(settings, db))
    app.mount('/blacklist',lookups.get_blacklist_app(settings, db))
    return app
