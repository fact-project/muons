import photon_stream as ps
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import binned_statistic_2d
from datetime import datetime as dt

dpi = 150
figw = 10
figh = 10
m = np.fromfile('muon.info', dtype=ps.muons.extraction.header_dtype)

print('Total number of muons', m.shape[0]/1e6, 'M muon events')


# suspicious time
# end = (57200-40587)*86400
# start = (57100-40587)*86400
# past_start = m['UnixTime_s'] > start
# before_end = m['UnixTime_s'] < end
# fine = past_start*before_end

# XY ring centers all time
#-------------------------
fnm = 'xy_ring_centers_all_time.png'
if not os.path.exists(fnm):
	bincounts, xbinedges, ybinedges = np.histogram2d(
		x=m['ring_center_x'],
		y=m['ring_center_y'],
		bins=[xbinedges, ybinedges])

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.imshow(
		bincounts, 
		extent=[
			xbinedges[0],
			xbinedges[-1],
			ybinedges[0],
			xbinedges[-1]
		],
		cmap='viridis'
	)
	fov_circle = plt.Circle((0, 0), 2.25, linewidth=0.2, edgecolor='r', fill=False, zorder=10)
	ax.add_artist(fov_circle)
	plt.title('muon ring center distribution')
	ax.xaxis.set_ticks_position('bottom')
	plt.xlabel('direction x/deg')
	plt.ylabel('direction y/deg')
	plt.colorbar()
	plt.savefig(fnm,dpi=dpi)
	plt.close()


# XY number of photons on full ring all time
#-------------------------------------------
fnm = 'xy_photon_count_on_full_ring_all_time.png'
if not os.path.exists(fnm):
	h1,h2,h3,h4 = binned_statistic_2d(
		m['ring_center_x'],
		m['ring_center_y'],
		values=m['number_muon_photons']/m['ring_overlap_with_fov'],
		statistic='mean', 
		bins=[xbinedges,ybinedges])

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.imshow(
		h1, 
		extent=[
			xbinedges[0],
			xbinedges[-1],
			ybinedges[0],
			xbinedges[-1]
		],
		cmap='viridis'
	)
	fov_circle = plt.Circle((0, 0), 2.25, linewidth=0.2, edgecolor='r', fill=False, zorder=10)
	ax.add_artist(fov_circle)
	plt.title('reconstructed number of photons on full muon ring')
	ax.xaxis.set_ticks_position('bottom')
	plt.xlabel('direction x/deg')
	plt.ylabel('direction y/deg')
	plt.colorbar()
	plt.savefig(fnm,dpi=dpi)
	plt.close()


# XY number of photons all time
#------------------------------
fnm = 'xy_photon_count_all_time.png'
if not os.path.exists(fnm):
	h1,h2,h3,h4 = binned_statistic_2d(
		m['ring_center_x'],
		m['ring_center_y'],
		values=m['number_muon_photons'],
		statistic='mean', 
		bins=[xbinedges,ybinedges])

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.imshow(
		h1, 
		extent=[
			xbinedges[0],
			xbinedges[-1],
			ybinedges[0],
			xbinedges[-1]
		],
		cmap='viridis'
	)
	fov_circle = plt.Circle((0, 0), 2.25, linewidth=0.2, edgecolor='r', fill=False, zorder=10)
	ax.add_artist(fov_circle)
	plt.title('number of photons on visible muon ring')
	ax.xaxis.set_ticks_position('bottom')
	plt.xlabel('direction x/deg')
	plt.ylabel('direction y/deg')
	plt.colorbar()
	ax.add_artist(fov_circle)
	plt.savefig(fnm,dpi=dpi)
	plt.close()


# XY arrival_time all time
#------------------------------
fnm = 'xy_arrival_time_all_time.png'
if not os.path.exists(fnm):

	cut_max_arr_time = 3e-8
	valid = m['arrival_time'] < cut_max_arr_time

	h1,h2,h3,h4 = binned_statistic_2d(
		m['ring_center_x'][valid],
		m['ring_center_y'][valid],
		values=m['arrival_time'][valid],
		statistic='mean', 
		bins=[xbinedges,ybinedges])

	#notnan = np.logical_not(np.isnan(h1))
	h5 = h1 - np.nanmin(h1)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.imshow(
		h5, 
		extent=[
			xbinedges[0],
			xbinedges[-1],
			ybinedges[0],
			xbinedges[-1]
		],
		cmap='viridis'
	)
	plt.colorbar()
	fov_circle = plt.Circle((0, 0), 2.25, linewidth=0.2, edgecolor='r', fill=False, zorder=10)
	ax.add_artist(fov_circle)
	plt.title('(mean relative arrival time of muon ring)/s')
	ax.xaxis.set_ticks_position('bottom')
	plt.xlabel('direction x/deg')
	plt.ylabel('direction y/deg')
	plt.savefig(fnm,dpi=dpi)
	plt.close()



# Ring Radius histogram
#------------------------------
fnm = 'ring_radius_histogram_all_time.png'
if not os.path.exists(fnm):
	min_radius = np.min(m['ring_radius'])
	max_radius = np.max(m['ring_radius'])
	nbins = int(0.1*np.sqrt(m.shape[0]))
	step = (max_radius - min_radius)/nbins
	binedges = np.linspace(min_radius, max_radius, nbins)
	bincounts, binedges = np.histogram(m['ring_radius'], bins=binedges)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.step(binedges[0:-1], bincounts)
	plt.title('muon ring radius distribution, bin width '+str(round(1e3*step,3))+'mdeg')
	plt.xlabel('muon ring radius/deg')
	plt.ylabel('intensity/1')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


# Ring overlap histogram
#------------------------------
fnm = 'ring_overlap_histogram_all_time.png'
if not os.path.exists(fnm):
	nbins = int(0.1*np.sqrt(m.shape[0]))
	step = 0.99/nbins
	binedges = np.linspace(0, 0.99, nbins)
	bincounts, binedges = np.histogram(m['ring_overlap_with_fov'], bins=binedges)
	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.step(binedges[0:-1], bincounts)
	plt.title('full overlap is excluded here')
	plt.xlabel('ring_overlap_with_fov/1')
	plt.ylabel('intensity/1')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


# arrival time histogram
#------------------------------
fnm = 'arrival_time_histogram_all_time.png'
if not os.path.exists(fnm):
	min_t = np.min(m['arrival_time'])
	max_t = np.max(m['arrival_time'])
	nbins = int(0.1*np.sqrt(m.shape[0]))
	step = (max_t - min_t)/nbins
	binedges = np.linspace(min_t, max_t, nbins)
	bincounts, binedges = np.histogram(m['arrival_time'], bins=binedges)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.step(binedges[0:-1], bincounts)
	plt.title('arrival time distribution, bin width '+str(round(1e12*step,3))+'ps')
	plt.xlabel('arrival time/s')
	plt.ylabel('intensity/1')
	plt.savefig(fnm,dpi=dpi)
	plt.semilogy()
	plt.savefig('log_'+fnm,dpi=dpi)
	plt.close()


# event_number histogram
#------------------------------
fnm = 'event_number_histogram_all_time.png'
if not os.path.exists(fnm):
	min_t = np.min(m['Event'])
	max_t = np.max(m['Event'])
	nbins = int(0.1*np.sqrt(m.shape[0]))
	step = (max_t - min_t)/nbins
	binedges = np.linspace(min_t, max_t, nbins)
	bincounts, binedges = np.histogram(m['Event'], bins=binedges)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.step(binedges[0:-1], bincounts)
	plt.xlabel('Event number/1')
	plt.ylabel('intensity/1')
	plt.savefig(fnm,dpi=dpi)
	plt.semilogy()
	plt.savefig('log_'+fnm,dpi=dpi)
	plt.close()

# run_number histogram
#------------------------------
fnm = 'run_number_histogram_all_time.png'
if not os.path.exists(fnm):
	min_t = np.min(m['Run'])
	max_t = np.max(m['Run'])
	nbins = int(0.01*np.sqrt(m.shape[0]))
	step = (max_t - min_t)/nbins
	binedges = np.linspace(min_t, max_t, nbins)
	bincounts, binedges = np.histogram(m['Run'], bins=binedges)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.step(binedges[0:-1], bincounts)
	plt.xlabel('Run number/1')
	plt.ylabel('intensity/1')
	plt.savefig(fnm,dpi=dpi)
	plt.semilogy()
	plt.savefig('log_'+fnm,dpi=dpi)
	plt.close()


# Ring Radius histogram vs time
#------------------------------
fnm = 'ring_radius_histogram_vs_time'
if not os.path.exists(fnm+'0.png'):
	min_radius = np.min(m['ring_radius'])
	max_radius = np.max(m['ring_radius'])
	nbins1 = int(np.sqrt(m.shape[0]))
	ntimebins = 64
	nbins = int(nbins1/ntimebins)
	step = (max_radius - min_radius)/nbins
	binedges = np.linspace(min_radius, max_radius, nbins)
	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	time_bin_edges = np.linspace(start, end, ntimebins)
	time_bin_idx = np.digitize(m['UnixTime_s'], bins=time_bin_edges)

	for t in range(ntimebins-1):
		radii_in_time_range = m['ring_radius'][time_bin_idx==t]
		bincounts, binedges = np.histogram(radii_in_time_range, bins=binedges)

		fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
		plt.step(binedges[0:-1], bincounts/radii_in_time_range.shape[0])
		plt.title('muon ring radius distribution, bin width '+str(round(1e3*step,3))+'mdeg\n from '+dt.fromtimestamp(time_bin_edges[t]).strftime('%Y-%m-%d')+' to '+dt.fromtimestamp(time_bin_edges[t+1]).strftime('%Y-%m-%d'))
		plt.ylim([0.0, 0.06])
		plt.xlabel('muon ring radius/deg')
		plt.ylabel('intensity/normalized')
		plt.savefig(fnm+str(t)+'.png',dpi=dpi)
		plt.close()


#------------------------------
fnm = 'number_photons_vs_arrival_time.png'
if not os.path.exists(fnm):
	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['number_muon_photons'], 
		m['arrival_time'],
		bins=[
			np.linspace(25, 400, 375),
			np.linspace(1e-8, 3e-8, 1000),
		],
		cmap='viridis')
	plt.colorbar()
	plt.xlabel('number_muon_photons/1')
	plt.ylabel('arrival_time/s')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'number_photons_vs_ring_radius.png'
if not os.path.exists(fnm):
	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['number_muon_photons'], 
		m['ring_radius'],
		bins=[
			np.linspace(25, 400, 375),
			np.linspace(.5, 1.5, 1000),
		],
		cmap='viridis')
	plt.colorbar()
	plt.xlabel('number_muon_photons/1')
	plt.ylabel('ring_radius/deg')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'number_photons_vs_ring_radius.png'
if not os.path.exists(fnm):
	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['number_muon_photons'], 
		m['ring_radius'],
		bins=[
			np.linspace(25, 400, 375),
			np.linspace(.5, 1.5, 1000),
		],
		cmap='viridis')
	plt.colorbar()
	plt.xlabel('number_muon_photons/1')
	plt.ylabel('ring_radius/deg')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'arrival_time_vs_ring_radius.png'
if not os.path.exists(fnm):
	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['arrival_time'],
		m['ring_radius'], 
		bins=[
			np.linspace(1e-8, 3e-8, 1000),
			np.linspace(0.5, 1.5, 1000)
		],
		cmap='viridis')
	plt.colorbar()
	#plt.title('muon ring radius distribution, bin width '+str(round(1e3*step,3))+'mdeg')
	plt.xlabel('arrival_time/s')
	plt.ylabel('ring_radius/deg')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'date_vs_number_photons.png'
if not os.path.exists(fnm):

	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	ntimebins = 1000
	time_bin_edges = np.linspace(start, end, ntimebins)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['UnixTime_s'],
		m['number_muon_photons'], 
		bins=[
			time_bin_edges,
			np.linspace(25, 400, 375)
		],
		cmap='viridis')
	plt.colorbar()
	plt.xlabel('UnixTime/s')
	plt.ylabel('number_muon_photons/1')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'date_vs_ring_radius.png'
if not os.path.exists(fnm):

	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	ntimebins = 1000
	time_bin_edges = np.linspace(start, end, ntimebins)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['UnixTime_s'],
		m['ring_radius'], 
		bins=[
			time_bin_edges,
			np.linspace(0.5, 1.5, 1000)
		],
		cmap='viridis')
	plt.colorbar()
	plt.xlabel('UnixTime/s')
	plt.ylabel('ring_radius/deg')
	plt.savefig(fnm,dpi=dpi)
	plt.close()

#------------------------------
fnm = 'date_vs_arrival_time.png'
if not os.path.exists(fnm):

	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	ntimebins = 1000
	time_bin_edges = np.linspace(start, end, ntimebins)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['UnixTime_s'], 
		m['arrival_time'],
		bins=[
			time_bin_edges,
			np.linspace(1.5e-8, 3e-8, 1000),
		],
		cmap='viridis')
	plt.colorbar()
	plt.title('main bulk of arrival times')
	plt.xlabel('UnixTime/s')
	plt.ylabel('arrival_time/s')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'date_vs_late_arrival_time.png'
if not os.path.exists(fnm):

	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	ntimebins = 100
	time_bin_edges = np.linspace(start, end, ntimebins)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['UnixTime_s'], 
		m['arrival_time'],
		bins=[
			time_bin_edges,
			np.linspace(3e-8, 7e-8, 100),
		],
		cmap='viridis')
	plt.colorbar()
	plt.title('late arrival times past 3e-8s')
	plt.xlabel('UnixTime/s')
	plt.ylabel('arrival_time/s')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'date_vs_ring_overlap_with_fov.png'
if not os.path.exists(fnm):

	start = m['UnixTime_s'].min()
	end = m['UnixTime_s'].max()
	ntimebins = 1000
	time_bin_edges = np.linspace(start, end, ntimebins)

	fig, ax = plt.subplots(figsize=(figw,figh), dpi=dpi)
	plt.hist2d(
		m['UnixTime_s'], 
		m['ring_overlap_with_fov'],
		bins=[
			time_bin_edges,
			np.linspace(0, 0.99, 1000),
		],
		cmap='viridis')
	plt.colorbar()
	plt.title('Ring overlap with fov vs date\nexcluding full overlap')
	plt.xlabel('UnixTime/s')
	plt.ylabel('ring overlap/1')
	plt.savefig(fnm,dpi=dpi)
	plt.close()


#------------------------------
fnm = 'rates.png'
if not os.path.exists(fnm):
	night = -1
	run = -1
	new_run = False
	events_in_run = 0
	start = 0
	for event in m:
		if event['Night'] > night:
			night = event['Night']
			run = event['Run']
			new_run = True

		if event['Run'] > run:
			run = event['Run']
			new_run = True

		if new_run:
			print(night, run, events_in_run)
			start = event['UnixTime']
			new_run = False
			events_in_run = 0
		else:
			events_in_run += 1


