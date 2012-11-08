
from bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request, hook, static_file
import job
import lookups
import buildd
import package
import packageinstance

def get_app(settings, db):
    app = Bottle(config={'settings' : settings, 'db' : db})
    @app.error(404)
    def error404(error):
        return 'HTTP Error 404 - Not Found.'
    
    # Remove this to get more debug.
    @app.error(500)
    def error500(error):
        return 'HTTP Error 500 - Internal Server Error.'
    
    # Things in here are applied to all requests. We need to set this header so strict browsers can query it using jquery
    #http://en.wikipedia.org/wiki/Cross-origin_resource_sharing
    @app.hook('after_request')
    def enable_cors():
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    @app.route('/', method='GET')
    def index():
        return template("pybitweb/static/index.htm",
                        host=settings['web']['hostname'],
                        port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    @app.route('/settings.json', method='GET')
    def js_settings():
        response.content_type = "application/json"
        return static_file("settings.json", root='./pybitweb/static/')
    
    # static resources like CSS
    @app.route('/bootstrap/<filepath:path>', method='GET')
    def serve_static_res(filepath):
            return static_file(filepath, root='./pybitweb/static/bootstrap/')
    
    # static HTML index page
    @app.route('/index.htm', method='GET')
    def serve_static_idex():
            return template("pybitweb/static/index.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    # static HTML page listing buildboxes
    @app.route('/buildd.htm', method='GET')
    def serve_static_buildboxes():
            return template("pybitweb/static/buildd.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    # static HTML page listing jobs
    @app.route('/job.htm', method='GET')
    def serve_static_jobs():
            return template("pybitweb/static/job.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    # static HTML page listing things
    @app.route('/lookups.htm', method='GET')
    def serve_static_lookups():
            return template("pybitweb/static/lookups.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    # static HTML page listing packages
    @app.route('/package.htm', method='GET')
    def serve_static_packages():
            return template("pybitweb/static/package.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    
    # static HTML page listing package instances
    @app.route('/packageinstance.htm', method='GET')
    def serve_static_package_instances():
            return template("pybitweb/static/packageinstance.htm",
                            host=settings['web']['hostname'],
                            port=settings['web']['port'],
                        protocol=settings['web']['protocol'])
    app.mount('/job', job.get_job_app(settings, db))
    app.mount('/suite', lookups.get_suite_app(settings, db))
    app.mount('/suitearch', lookups.get_suite_app(settings, db))
    app.mount('/dist', lookups.get_dist_app(settings, db))
    app.mount('/status',lookups.get_status_app(settings, db))
    app.mount('/arch',lookups.get_arch_app(settings, db))
    app.mount('/format', lookups.get_format_app(settings, db))
    app.mount('/buildd', buildd.get_buildd_app(settings, db))
    app.mount('/package', package.get_packages_app(settings, db))
    app.mount('/packageinstance', packageinstance.get_packageinstance_app(settings, db))
    return app