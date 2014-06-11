from pyramid.exceptions import NotFound
from pyramid.renderers import get_renderer
from pyramid.view import view_config

from aamm import Manager
import config

class AAMMViews(object):
    def __init__(self, request):
        self.request = request
        renderer = get_renderer("templates/layout.pt")
        self.layout = renderer.implementation().macros['layout']
        self.aamm = Manager(config.server, config.port,
                config.username, config.password, config.tz_offset)

    @view_config(route_name='home', renderer='templates/index.pt')
    def home(self):
        return dict(title='Protected Machines')

    @view_config(route_name='machine_view', renderer='templates/machine_view.pt')
    def machine_view(self):
        machine = self.request.matchdict['machine']
        machine_name = self.request.matchdict['machine_name']
        try:
            return dict(title=machine_name, machine=machine)
        except KeyError:
            raise NotFound

    @view_config(route_name='mount_do', renderer='templates/mount_do.pt')
    def mount_do(self):
        machine_id = self.request.matchdict['machine_id']
        machine_name = self.request.matchdict['machine_name']
        recovery_point_id = self.request.matchdict['point_id']
        recovery_point_time = self.request.matchdict['point_time']
        volume_ids = self.request.matchdict['volume_ids'].split(' ')
        try:
            point = self.aamm.mount_recovery_point(recovery_point_id,
                        recovery_point_time, machine_id, machine_name,
                        volume_ids)
            if point and 'is already being used' in point:
                return dict(title=machine_name,
                        recovery_point='Error: this path is already mounted.')
            elif point:
                raise KeyError
            return dict(title=machine_name, recovery_point=point)
        except KeyError:
            raise NotFound

    # API

    @view_config(route_name='api', renderer='prettyjson')
    def api(self):
        try:
            return self.aamm.get_machines()
        except KeyError:
            raise NotFound

    @view_config(route_name='machine_api', renderer='prettyjson')
    def machine_api(self):
        machine = self.request.matchdict['machine']
        try:
            _, recovery_points = self.aamm.get_recovery_points(machine)
            return recovery_points
        except KeyError:
            raise NotFound

def notfound(request):
    request.response.status = 404
    return dict(title='No Such Machine')
