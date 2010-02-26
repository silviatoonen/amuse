import os
import sys
import numpy

try:
    from matplotlib import pyplot
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    
from amuse.legacy.fi import interface as interface
from amuse.ext.evrard_test import MakeEvrardTest
from amuse.ext.evrard_test import regular_grid_unit_cube
from amuse.ext.evrard_test import body_centered_grid_unit_cube
from amuse.legacy.support.channel import MessageChannel
import path_to_test_results
from amuse.legacy.support.core import is_mpd_running

MessageChannel.no_redirection()

def energy_plot(time,ek,ep,eth):
  if not HAS_MATPLOTLIB:
    return
    
  pyplot.figure(figsize = (5, 5))
  pyplot.xlabel(r'time')
  pyplot.ylabel(r'energy')
  pyplot.plot(time,ek)
  pyplot.plot(time,ep)
  pyplot.plot(time,eth)
  pyplot.plot(time,ek+ep+eth)
  test_results_path = path_to_test_results.get_path_to_test_results()
  pyplot.savefig(os.path.join(test_results_path, "evrard_test.png"))

def run_evrard(x):
  evrard=MakeEvrardTest(x)
  mass,x,y,z,vx,vy,vz,u=evrard.new_model()
  smooth=numpy.zeros_like(mass)

  nb = interface.fi()
  nb.setup_module()

  nb.set_stepout(99999)
  nb.set_steplog(99999)
  nb.set_usesph(0)
  nb.set_radiate(1)
  nb.set_dtime(0.05)
  nb.set_gdgop(0)
  nb.set_uentropy(0)
  nb.set_verbosity(0)
    
  ids,error = nb.new_sph_particle(mass,smooth,x,y,z,vx,vy,vz,u)
  if filter(lambda x: x != 0, error) != []: raise Exception

  nb.initialize_particles(0.0)

  if hasattr(nb,"viewer"):
    nb.viewer()

  dt=0.05
  tnow=0.
  nb.synchronize_model()
  time,Ek,Ep,Eth=[],[],[],[]
  time.append(tnow)
  e,ret=nb.get_kinetic_energy()
  Ek.append(e)
  e,ret=nb.get_potential_energy()
  Ep.append(e)
  e,ret=nb.get_thermal_energy()
  Eth.append(e)
  while tnow<3.0:
    tnow=tnow+dt
    nb.evolve(tnow)
    nb.synchronize_model()
    tnow,err=nb.get_time()
    time.append(tnow)
    e,ret=nb.get_kinetic_energy()
    Ek.append(e)
    e,ret=nb.get_potential_energy()
    Ep.append(e)
    e,ret=nb.get_thermal_energy()
    Eth.append(e)

  nb.cleanup_module()

  del nb
 
  time=numpy.array(time)
  Ek=numpy.array(Ek)
  Ep=numpy.array(Ep)
  Eth=numpy.array(Eth)
  energy_plot(time,Ek,Ep,Eth)

def test_evrard():
  if not is_mpd_running():
      return
  run_evrard(64)
    
if __name__=="__main__":
  run_evrard(1000)
