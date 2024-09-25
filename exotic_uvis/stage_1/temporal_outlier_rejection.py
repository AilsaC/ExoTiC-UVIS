import numpy as np
from tqdm import tqdm
from exotic_uvis.plotting import plot_exposure, plot_corners

def fixed_iteration_rejection(obs, sigmas=[10,10], replacement=None,
                              verbose = 0, show_plots = 0, save_plots = 0, output_dir = None):
    '''
    Iterates a fixed number of times using a different sigma at each iteration to reject cosmic rays.

    :param obs: xarray. Its obs.images DataSet contains the images.
    :param sigmas: lst of int. Sigma to use for each iteration. len(sigmas) is the number of iterations that will be run.
    :param_replacement: int or None. If None, replace outlier pixels with median in time. If int, replace with median of int values either side in time.
    :return: obs with cosmic rays removed.
    '''
    # Copy images and define hit map.
    images = obs.images.data.copy()
    hit_map = np.zeros_like(images)

    # Track pixels corrected.
    bad_pix_removed = 0
    # Iterate over each sigma.
    for j, sigma in enumerate(sigmas):
        # Get the median time frame and std as a reference.
        med = np.median(images,axis=0)
        std = np.std(images,axis=0)

        # Track outliers flagged by this sigma.
        bad_pix_this_sigma = 0

        # Then check over frames and see where outliers are.
        for k in tqdm(range(images.shape[0]), desc = "Correcting for %.0fth sigma... Progress:" % j):
            # Get the frame and dq array as np.array objects so we can operate on them.
            d = images[k]
            S = np.where(np.abs(d - med) > sigma*std, 1, 0)
            
            # Report where data quality flags should be added and count pixels to be replaced.
            dq = np.where(S != 0, 1, 0)
            hit_map[k,:,:] += dq
            bad_pix_this_frame = np.count_nonzero(S)
            bad_pix_this_sigma += bad_pix_this_frame

            # If replacement is not None, custom replacement.
            correction = med
            if replacement:
                # Take the median of the frames that are +/- replacement away from the current frame.
                l = k - replacement
                r = k + replacement
                # Cut at edges.
                if l < 0:
                    l = 0
                if r > images.shape[0]:
                    r = images.shape[0]
                correction = np.median(images[l:r,:,:],axis=0)
            # Correct frame and replace in images.
            images[k] = np.where(S == 1, correction, d)
        
        print("Bad pixels removed on iteration %.0f with sigma %.2f: %.0f" % (j, sigma, bad_pix_this_sigma))
        bad_pix_removed += bad_pix_this_sigma
    
    # Correct hit map.
    hit_map[hit_map != 0] = 1
    print("All iterations complete. Total pixels corrected: %.0f out of %.0f" % (bad_pix_removed, S.shape[0]*S.shape[1]))

    # if true, plot one exposure and draw location of all detected cosmic rays in all exposures
    if save_plots > 0 or show_plots > 0:
        thits, xhits, yhits = np.where(hit_map == 1)
        plot_exposure([obs.images.data[0], images[0]], min = 0, 
                      title = 'Temporal Bad Pixel removal Example', 
                      show_plot=show_plots, save_plot=save_plots,
                      stage=1, output_dir=output_dir,
                      filename = ['Before_CR_correction', 'After_CR_correction'])

        plot_exposure([obs.images.data[0]], scatter_data=[yhits, xhits], min = 0, 
                      title = 'Location of corrected pixels', mark_size = 1,
                      show_plot=show_plots, save_plot=save_plots, 
                      stage=1, output_dir=output_dir, filename = ['CR_location'])

    # if true, check each exposure separately
    if save_plots == 2:
        for i in range(len(images)):
            xhits, yhits = np.where(hit_map[i] == 1)
            plot_exposure([obs.images.data[i]], scatter_data=[yhits, xhits], min = 0,
                          title = 'Location of corrected pixels', mark_size = 1,
                          show_plot=show_plots, save_plot=save_plots, 
                          stage=1, output_dir=output_dir, filename = [f'CR_location_frame{i}'])
            
    # modify original images and dq
    obs.images.data = images
    obs.data_quality.data = np.where(hit_map != 0, hit_map, obs.data_quality.data)

    return obs


def array1D_clip(array, threshold = 3.5, mode = 'median'): 
    """Function to detect and replace outliers in a 1D array above or below a certain sigma threshold imposed

    Args:
        array (_type_): _description_
        threshold (float, optional): _description_. Defaults to 3.5.
        mode (str, optional): _description_. Defaults to 'median'.

    Returns:
        _type_: _description_
    """
    
    # define outlier flag and mask
    found_outlier = 1
    mask = np.ones_like(array).astype(bool)

    # iterate while flag is true
    while found_outlier:
        
        # compute median and std of masked array
        n_hits = np.sum(mask)
        median = np.median(array[mask])
        sigma = np.std(array[mask])

        # mask values below threshold
        mask = np.abs(array - median) < threshold * sigma     
        found_outlier = n_hits - np.sum(mask)
    
    # replace masked values with median
    array[~mask] = median

    return array, ~mask


def free_iteration_rejection(obs, threshold = 3.5,
                             verbose = 0, show_plots = 0, save_plots = 0, output_dir = None):
    """Function to replace outliers in the temporal dimension

    Args:
        obs (_type_): _description_
        threshold (float, optional): _description_. Defaults to 3.5.
        verbose (int, optional): _description_. Defaults to 0.
        show_plots (int, optional): _description_. Defaults to 0.
        save_plots (int, optional): _description_. Defaults to 0.
        output_dir (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    # copy images and define hit map
    images = obs.images.data.copy()
    hit_map = np.zeros_like(images)

    # iterate over all rows
    for i in tqdm(range(obs.dims['x']), desc = 'Removing cosmic rays and bad pixels... Progress:'):

        #iterate over all columns
        for j in range(obs.dims['y']):
            
            # check that sum of pixel along temporal dimension is non-zero (i.e., that the pixel is inside the subarray)
            if np.sum(images[:, i, j]):
                _, hit_map[:, i, j] = array1D_clip(images[:, i, j], threshold, mode = 'median')
    
    # if true, plot one exposure and draw location of all detected cosmic rays in all exposures
    if save_plots > 0 or show_plots > 0:
        thits, xhits, yhits = np.where(hit_map == 1)
        plot_exposure([obs.images.data[0], images[0]], min = 1e0, 
                      title = 'Temporal Bad Pixel removal Example', 
                      show_plot=show_plots, save_plot=save_plots,
                      stage=1, output_dir=output_dir,
                      filename = ['Before_CR_correction', 'After_CR_correction'])

        plot_exposure([obs.images.data[0]], scatter_data=[yhits, xhits], min = 1e0, 
                      title = 'Location of corrected pixels', mark_size = 1,
                      show_plot=show_plots, save_plot=save_plots, 
                      stage=1, output_dir=output_dir, filename = ['CR_location'])

    # if true, check each exposure separately
    if save_plots == 2:
        for i in range(len(images)):
            xhits, yhits = np.where(hit_map[i] == 1)
            plot_exposure([obs.images.data[i]], scatter_data=[yhits, xhits], min = 1e0,
                          title = 'Location of corrected pixels', mark_size = 1,
                          show_plot=show_plots, save_plot=save_plots, 
                          stage=1, output_dir=output_dir, filename = [f'CR_location_frame{i}'])
    
    # modify original images
    obs.images.data = images

    return obs