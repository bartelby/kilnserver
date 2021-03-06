import socket, json
from kilncontroller import constants
from kilnweb.model import db, Job, JobStep
from collections import OrderedDict

SOCK_PATH = constants.SOCK_PATH

def jdefault(o):
  if isinstance(o, JobStep):
    d = OrderedDict()
    for key in o.__mapper__.c.keys():
      d[key] = o[key]
    return d
  return o.__dict__

class KilnCommand:
  def __init__(self):
    self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    self.sock.connect(SOCK_PATH)

  def __del__(self):
    self.sock.close()

  def start(self, job_id):
    # TODO: Handle job not found condition
    job = Job.query.filter_by(id=int(job_id)).first()
    command = json.dumps({'command': 'start', 'job_id': int(job_id), 'steps': job.steps}, default=jdefault)
    self.sock.sendall(command + "\n")

  def stop(self):
    command = json.dumps({'command': 'stop'})
    self.sock.sendall(command + "\n")

  def pause(self):
    command = json.dumps({'command': 'pause'})
    self.sock.sendall(command + "\n")

  def resume(self):
    command = json.dumps({'command': 'resume'})
    self.sock.sendall(command + "\n")

  def status(self):
    state = None
    job_id = None
    command = json.dumps({'command': 'status'})
    self.sock.sendall(command + "\n")
    data = self.sock.recv(1024)
    if data:
      status_data = json.loads(data)
      state = status_data['state']
      job_id = status_data['job_id']
    return [state,job_id]

