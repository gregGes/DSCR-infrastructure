__author__ = 'visti'
import base64
from datetime import datetime
from datetime import timedelta
import uuid
import requests
import copy
import xml.etree.ElementTree as ElT
from time import sleep


class CBError(Exception):
    def __init__(self, q):
        if q is None:
            self.status_code = 42
        else:
            print q.status_code
            print q.text
            self.status_code = q.status_code

    def __str__(self):
        return repr(self.status_code)


class Instance(object):
    def __init__(self, app=None, waitfor=None, fl=None):
        if app is None:
            raise CBError(None)
        self.app = app
        self.waitfor = waitfor

        self.files = fl
        self.active = None


class Application(object):
    def __init__(self, sname, ename, param_template=None):
        self.sname = sname
        self.executable = ename
        self.param_template = param_template


class Service(object):
    def __init__(self, application, cloud, flavour):
        """

        :param application: Application to run
        :param cloud: Cloud service provider
        :param flavour: Instance size
        All reference to cloudsetup.xml
        """
        x = ElT.Element("job")
        y = ElT.SubElement(x, "software_name")
        y.text = application.sname
        y = ElT.SubElement(x, "executable-name")
        y.text = application.executable
        y = ElT.SubElement(x, "resource-name")
        y.text = cloud.provider
        y = ElT.SubElement(x, "region-name")
        y.text = cloud.region
        y = ElT.SubElement(x, "instance-type-name")
        y.text = flavour

        self.shutdown_instance = copy.deepcopy(x)
        z = ElT.SubElement(self.shutdown_instance, "argument_string")
        z.text = "shutdown"

        y = ElT.SubElement(x, "no-instance-shutdown")
        y.text = "false"

        self.instance = x
        self.arg_template = application.param_template


class Cloud(object):
    def __init__(self, provider, region):
        self.provider = provider
        self.region = region
        self.flavours = {}


class BasicData(object):
    def __init__(self, url, pwfile, picklefile, setupfile):
        self.picklefile = picklefile
        with open(pwfile, "r") as tf:
            self.username = tf.readline().replace('\n', '')
            self.password = tf.readline().replace('\n', '')
        self.url = url

        self.bs_cred = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')

        self.environment = {}
        self.clouds = {}
        self.applications = {}
        cloud_setup = None
        with open(setupfile, "r") as sf:
            setup_xml = ElT.fromstring(sf.read())
        try:
            cloud_setup = setup_xml.find("clouds")
        except AttributeError:
            print("no clouds")
            ElT.dump(setup_xml)
        for cloud in cloud_setup:
            this_cloud_name = ""
            this_cloud_provider = ""
            this_cloud_region = ""
            try:
                this_cloud_name = cloud.find("name").text
                this_cloud_provider = cloud.find("provider").text
                this_cloud_region = cloud.find("region").text
            except AttributeError:
                print ("malformed xml file n/p/r")
                ElT.dump(cloud)
                exit(1)
            nc = Cloud(this_cloud_provider, this_cloud_region)
            self.clouds[this_cloud_name] = nc
            try:
                for fl_list in cloud.find("flavours"):
                    this_flavour_name = fl_list.find("size").text
                    this_flavour_id = fl_list.find("id").text
                    self.clouds[this_cloud_name].flavours[this_flavour_name] = this_flavour_id
            except AttributeError:
                print ("malformed xml %s flavours" % this_cloud_name)
                ElT.dump(cloud)
                exit(1)
        app_setup = None
        try:
            app_setup = setup_xml.find("applications")
        except AttributeError:
            print ("no applications")
            ElT.dump(setup_xml)
            exit(1)
        for app in app_setup:
            this_app_name = None
            this_software = None
            this_executable = None

            try:
                this_app_name = app.find("name").text
                this_software = app.find("sname").text
                this_executable = app.find("executable").text
            except AttributeError:
                print("malformed app")
                ElT.dump(app_setup)
                exit(1)
            try:
                this_parameters = app.find("param_template").text
            except AttributeError:
                this_parameters = None
            new_app = Application(this_software, this_executable, this_parameters)
            self.applications[this_app_name] = new_app

    def add_environment(self, cloud, tag, provider, region, size):
        pass

    def get_environment(self, cloud, tag):
        pass


class CloudbrokerConnection(object):
    def __init__(self, bd):
        self.session = requests.Session()
        self.bd = bd
        self.session.auth = (self.bd.username, self.bd.password)
        self.software = {}
        self.executable = {}
        self.query_executables()

    def c_url(self, url):
        return "%s/%s" % (self.bd.url, url)

    def make_query(self, qurl, parm={}):
        q = self.session.get(self.c_url(qurl), params=parm)

        if q.status_code < 400:
            pass
        else:
            raise CBError(q)
        rtr = ElT.fromstring(q.text)

        if rtr.tag == "errors":
            print q.text
            exit(1)
        return rtr

    def query_instances(self):
        r = self.make_query("/instances.xml")
        return r

    def query_job(self, jobid):
        url_ext = "jobs/%s.xml" % jobid
        q = self.make_query(url_ext)
        return q

    def query_executables(self):
        url_ext = "/softwares.xml"
        q = self.make_query(url_ext)
        for s in q:
            if s.find("status").text == "active":
                self.software[s.find("id").text] = s.find("name").text
        url_ext = "/executables.xml"
        q = self.make_query(url_ext)
        for e in q:
            if e.find("active").text == "true":
                self.executable[e.find("id").text] = "%s %s" % (self.software[e.find("software-id").text], e.find("binary").text)

    def locate_executable(self, exid):
        try:
            return self.executable[exid]
        except KeyError:
            return None

class CloudbrokerJob(object):
    def __init__(self, bd, sw, tag, arg_string=None):
        """

        :param bd: Basicdata class instance
        :param sw: Instance class instance
        :param tag: Freeform tag to mark the current application
        :param arg_string: to be inserted to sw argument template

        This represents a cloudbroker job.

        """
        name = "dscr"+uuid.uuid4().hex
        self.headers = {'Content-type': 'application/xml'}
        self.bd = bd
        self.tag = tag
        self.job_name = name
        itmp = copy.deepcopy(sw.app.instance)
        y = ElT.SubElement(itmp, "name")
        y.text = name
        if arg_string is not None and sw.app.arg_template is not None:
            y = ElT.SubElement(itmp, "argument_string")
            y.text = sw.app.arg_template % arg_string
        self.software = itmp

        itmp = copy.deepcopy(sw.app.shutdown_instance)
        y = ElT.SubElement(itmp, "name")
        y.text = name
        self.shutdown_software = itmp

        self.jobid = ""
        self.data_types = {}
        self.sw = sw
        self.session = requests.Session()
        self.session.auth = (self.bd.username, self.bd.password)
        self.input_files = sw.files
        self.waitfor = sw.waitfor

        self.data_files = {}
        self.ext_ip = None
        self.int_ip = None

    def c_url(self, url):
        return "%s/%s" % (self.bd.url, url)

    def r_get_request(self, url, parm={}):
        q = self.session.get(self.c_url(url), params=parm)

        if q.status_code < 400:
            pass
        else:
            raise CBError(q)
        rtr = ElT.fromstring(q.text)

        if rtr.tag == "errors":
            print q.text
            exit(1)
        return rtr

    def init_request(self, tree, url):
        if tree is None:
            tree_string = ""
        else:
            tree_string = ElT.tostring(tree, encoding='utf8', method='xml')

        q = self.session.post(self.c_url(url), data=tree_string, headers=self.headers)

        if q.status_code < 400:
            pass
        else:
            raise CBError(q)

        result_tree = ElT.fromstring(q.text)
        try:
            c = result_tree.find("id")
            self.jobid = c.text
        except AttributeError:
            self.jobid = ""

    def upload_file(self, fpath):
        if self.jobid == "":
            print "No job id"
            return
        fname = fpath.rsplit("/")[-1]
        payload = {"job_id": self.jobid, "data_file_name": fname,
                   "archive": "false", "data_type_id": self.data_types["input"]}

        try:
            fc = {"data": open(fpath, "rb")}
        except IOError:
            print "file not found %s" % fname
            raise CBError(None)

        q = self.session.post(self.c_url("data_files.xml"), data=payload, files=fc)
        if q.status_code < 400:
            pass
        else:
            raise CBError(q)

        dt = ElT.fromstring(q.text)
        try:
            self.data_files[dt.find("data-file-name").text] = dt.find("id").text
        except (IndexError, AttributeError):
            print "File upload did not return ID"
            raise CBError(None)

    def delete_request(self, url):
        q = self.session.delete(url)
        if q.status_code < 400:
            pass
        else:
            raise CBError(q)

        return q.text

    def stop_job(self):
        url_ext = "jobs/%s/stop.xml" % self.jobid
        q = self.session.put(self.c_url(url_ext))
        if q.status_code < 400:
            pass
        else:
            print "%s stop failed - continuing" % self.jobid

    def launch_job(self):
        url_ext = "jobs/%s/submit.xml" % self.jobid
        q = self.session.put(self.c_url(url_ext))
        if q.status_code < 400:
            pass
        else:
            raise CBError(q)
        if self.waitfor == "external":
            try:
                self.wait_for_external_ip(5)
                return self.ext_ip
            except CBError:
                raise
        if self.waitfor == "internal":
            try:
                self.wait_for_internal_ip(5)
                return self.int_ip
            except CBError:
                raise
        return None

    def check_job_status(self):
        url_ext = "jobs/%s.xml" % self.jobid
        q = self.session.get(self.c_url(url_ext))
        if q.status_code < 400:
            pass
        else:
            dt = ElT.fromstring(q.text)
            try:
                emsg = dt.find("error").text
                if emsg == "404: record not found":
                    return "Enoexists"
            except (IndexError, AttributeError):
                pass
            raise CBError(q)

        dt = ElT.fromstring(q.text)

        try:
            result = dt.find("status").text
        except (IndexError, AttributeError):
            print "Job does not return status"
            raise CBError(None)
        return result

    def check_running_instance(self):
        """

        This checks a running job - chiefly to check when internal and/or external
        ip address is present.

        """
        url_ext = "instances.xml"
        payload = {"job_id": self.jobid}
        r = self.session.get(self.c_url(url_ext), params=payload)
        int_ip = None
        ext_ip = None
        dt_array = ElT.fromstring(r.text)
        for dt in dt_array:
            try:
                int_ip = dt.find("internal-ip-address").text
                if int_ip == "not allocated":
                    int_ip = None
            except (IndexError, AttributeError):
                int_ip = None

            try:
                ext_ip = dt.find("external-ip-address").text
                if ext_ip == "not allocated":
                    ext_ip = None
            except (IndexError, AttributeError):
                ext_ip = None

        self.int_ip = int_ip
        self.ext_ip = ext_ip

    def create_job(self):
        x = self.r_get_request("data_types.xml")

        for dt in x:
            self.data_types[dt.find("name").text] = dt.find("id").text
        try:
            self.init_request(self.software, "jobs.xml")
        except:
            raise

        for fi in self.input_files:
            if fi is not None:
                try:
                    self.upload_file(fi)
                except CBError:
                    raise

    def create_stopper_job(self):
        """

        This create a dummy job to stop a running instance. Regular jobs have "no instance shutdown"
        marked in them. The stopper job has this set false - it shuts down an instance of its kind.

        :raise: Any error that might occur when launching the instance is passed through
        """
        x = self.r_get_request("data_types.xml")

        for dt in x:
            self.data_types[dt.find("name").text] = dt.find("id").text
        try:
            self.init_request(self.shutdown_software, "jobs.xml")
        except:
            raise
        finally:
            self.waitfor = None

    def wait_until_complete(self):
        while True:
            job_status = self.check_job_status()
            if job_status == "completed" or job_status == "Enoexists":
                break
            self.check_running_instance()
            sleep(5)
        print "Job finished %s" % self.job_name
        self.shutdown()

    def wait_for_internal_ip(self, timeout=None):
        if self.int_ip is not None:
            return
        start_time = datetime.today()
        while True:
            self.check_running_instance()
            if self.int_ip is not None:
                break
            sleep(5)
            current_time = datetime.today()
            if timeout is not None:
                if current_time - start_time > timedelta(minutes=timeout):
                    raise CBError(None)

    def wait_for_external_ip(self, timeout=None):
        if self.ext_ip is not None:
            return
        start_time = datetime.today()
        while True:
            self.check_running_instance()
            if self.ext_ip is not None:
                break
            sleep(5)
            current_time = datetime.today()
            if timeout is not None:
                if current_time - start_time > timedelta(minutes=timeout):
                    raise CBError(None)

    def shutdown(self):
        shutdown_url = self.c_url("jobs")+"/"+self.jobid+".xml"
        self.delete_request(shutdown_url)
