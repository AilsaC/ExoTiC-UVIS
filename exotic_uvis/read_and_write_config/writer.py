import os

def write_config(config_dict, stage, outdir):
    '''
    Unpacks a dictionary and writes it out to a config file.

    :param config_dict: dict. The dictionary used to guide the execution of a Stage of ExoTiC-UVIS.
    :param stage: int from 0 to 5. Which Stage was executed, which sets the template of the config file.
    :param outdir: str. The path to where the config file is to be stored.
    :return: config .hustle file written to the outdir.
    '''
    # Unpack all keywords.
    keys = list(config_dict.keys())

    # Get correct print info.
    if stage == 0:
        header, subsection_headers, subsection_keys, subsection_comments = Stage0_info()
    if stage == 1:
        header, subsection_headers, subsection_keys, subsection_comments = Stage1_info()
    
    # And write.
    with open(os.path.join(outdir,"stage_{}_exoticUVIS.hustle".format(stage))) as f:
        # First, write the overall file header.
        f.write(header)
        f.write('\n\n')

        # Then, start parsing each step out (Setup, Step 1, Step 2, etc.).
        subsections = list(subsection_keys.keys())
        for i, subsection in enumerate(subsection):
            # Write the step name.
            f.write(subsection_headers[i])
            f.write('\n')
            # For every keyword and comment in that step...
            for keywords in subsection_keys[subsection]:
                # Write the keyword, its value, and the comment.
                for keyword in keywords:
                    f.write("{} {:-30} {}\n".format(keyword, config_dict[keyword], subsection_comments[keyword]))
            # A space between this step and the next step.
            f.write('\n')
        # Declare the file over.
        f.write("# ENDPARSE")
            

def Stage0_info():
    '''
    Specific keys and subsections for Stage 0.
    '''
    header = "# ExoTiC-UVIS config file for launching Stage 0: Data Handling"

    subsection_headers = ["# Setup for Stage 0",
                          "# Step 1: Download files from MAST",
                          "# Step 2: Organizing files",
                          "# Step 3: Locating the target star",
                          "# Step 4: Quality quicklook",]
    
    subsection_keys = {"Setup":["toplevel_dir",],
                       "Step 1":["do_download",
                                 "programID",
                                 "target_name",
                                 "extensions"],
                       "Step 2":["do_organize",
                                 "visit_number"],
                       "Step 3":["do_locate",
                                 "location"],
                       "Step 4":["do_quicklook",
                                 "gif_dir"],
                       }
    
    subsection_comments = {"Setup":["# Directory where you want your files to be stored after Stage 0 has run. This is where /specimages, /directimages, /visitfiles, and /miscfiles will be stored.",],
                           "Step 1":["# Bool. Whether to perform this step.",
                                     "# ID of the observing program you want to query data from On MAST, referred to as 'proposal_ID'.",
                                     "# Name of the target object you want to query data from. On MAST, referred to as 'target_name'.",
                                     "# lst of str or None. File extensions you want to download. If None, take all file extensions. Otherwise, take only the files specified. _flt.fits, _spt.fits recommended as minimum working case.",],
                           "Step 2":["# Bool. Whether to perform this step.",
                                     "# The visit number you want to operate on.",
                                     "# None or str. If you downloaded data in Step 1, leave this as None. If you have pre-downloaded data, please place all of it in filesfrom_dir. Don't sort it into sub-folders; ExoTiC-UVIS won't be able to find them if they are inside sub-folders!",],
                           "Step 3":["# Bool. Whether to perform this step.",
                                     "# None or tuple of float. Prior to running Stage 0, this will be None. After running Stage 0, a copy of this .hustle file will be made with this information included.",],
                           "Step 4":["# Bool. Whether to perform this step.",
                                     "# str. Where to save the quicklook gif to.",],
                           }
    return header, subsection_headers, subsection_keys, subsection_comments

def Stage1_info():
    '''
    Specific keys and subsections for Stage 1.
    '''
    header = "# ExoTiC-UVIS config file for launching Stage 1: Reduction"

    subsection_headers = ["# Setup for Stage 1",
                          "# Step 1: Read in the data",
                          "# Step 2: Reject cosmic rays with time iteration\n# Step 2a: Fixed iteration parameters",
                          "# Step 2b: Free iteration parameters",
                          "# Step 2c: Sigma clip parameters",
                          "# Step 3: Reject hot pixels with spatial detection\n# Step 3a: Laplacian Edge Detection parameters",
                          "# Step 3b: Spatial smoothing parameters",
                          "# Step 4: Background subtraction\n# Step 4a: full frame mode or median background subtraction",
                          "# Step 4b: corners mode or median background subtraction",
                          "# Step 4c: Column-by-column background subtraction",
                          "# Step 4d: Pagul+ 2023 background subtraction",
                          "# Step 5: Displacement estimation\n# Step 5a: Source center-of-mass tracking",
                          "# Step 5b: Background star tracking",
                          "# Step 6: Save outputs",]
    
    subsection_keys = {"Setup":["toplevel_dir",
                                "run_name"],
                       "Step 1":["verbose",],
                       "Step 2a":["do_fixed_iter",
                                 "fixed_sigmas",
                                 "replacement",],
                       "Step 2b":["do_free_iter",
                                  "free_sigma"],
                       "Step 2c":["do_sigma_clip",],
                       "Step 3a":["do_led",
                                  "led_threshold",
                                  "led_factor",
                                  "led_n",
                                  "fine_structure",
                                  "contrast_factor",],
                       "Step 3b":["do_smooth",],
                       "Step_4a":["do_full_frame",
                                  "full_value",],
                       "Step 4b":["do_corners",
                                  "box_width",
                                  "box_height",
                                  "corners_value"],
                       "Step 4c":["do_column",],
                       "Step 4d":["do_Pagul23",
                                  "path_to_Pagul23",
                                  "mask_parameter",
                                  "median_columns",],
                       "Step 5a":["do_0thtracking",],
                       "Step 5b":["do_bkg_stars",
                                  "bkg_stars_loc",],
                       "Step 6":["do_save",],
                       }
    
    subsection_comments = {"Setup":["# Directory where your Stage 0 files are stored. This folder should contain the specimages/, directimages/, etc. folders with your data.",
                                    "# Str. This is the name of the current run. It can be anything that does not contain spaces or special characters (e.g. $, %, @, etc.)."],
                           "Step 1":["# Int from 0 to 2. How often and how detailed you want the output log to be.",],
                           "Step 2a":["# Bool. Whether to use fixed iteration rejection to clean the timeseries.",
                                      "# lst of float. The sigma to reject outliers at in each iteration. The length of the list is the number of iterations.",
                                      "# int or None. If int, replaces flagged outliers with the median of values within +/-replacement indices of the outlier. If None, uses the median of the whole timeseries instead.",],
                           "Step 2b":["# Bool. Whether to use free iteration rejection to clean the timeseries.",
                                      "# float. The sigma to reject outliers at in each iteration. Iterates over each pixel's timeseries until no outliers at this sigma level are found.",],
                           "Step 2c":["# Bool. Whether to use sigma clipping rejection to clean the timeseries.",],
                           "Step 3a":["# Bool. Whether to use Laplacian Edge Detection rejection to clean the frames.",
                                      "# Float. The threshold parameter at which to kick outliers in LED. The lower the number, the more values will be replaced.",
                                      "# Int. The subsampling factor. Minimum value 2. Higher values increase computation time but aren't expected to yield much improvement in rejection.",
                                      "# Int. Number of times to do LED on each frame.",
                                      "# Bool. Whether to build a fine structure model, which can protect narrow bright features like traces from LED.",
                                      "# Float. If fine_structure is True, acts as the led_threshold for the fine structure step.",],
                           "Step 3b":["# Bool. Whether to use spatial smoothing rejection to clean the frames.",],
                           "Step 4a":["# Bool. Whether to subtract the background using the full frame mode or median.",
                                      "# Str. The value to extract from the histogram. Options are 'coarse', 'Gaussian', or 'median'.",],
                           "Step 4b":["# Bool. Whether to subtract the background using the frame corners mode or median.",
                                      "# Int. The width of the box to use for the background calculation.",
                                      "# Int. The height of the box to use for the background calculation.",
                                      "# Str. The value to extract from the histogram. Options are 'coarse', 'Gaussian', or 'median'.",],
                           "Step 4c":["# Bool. Whether to subtract the background using a column-by-column method.",],
                           "Step 4d":["# Bool. Whether to subtract the background using the scaled Pagul+ 2023 G280 sky image.",
                                      "# Str. The absolute path to where the Pagul+ 2023 G280 sky image is stored.",
                                      "# Float. How strong the trace masking should be. Values of 0.001 or less recommended.",
                                      "# Bool. If True, takes the median value of each column in the Pagul+ 2023 sky image as the background. As the Pagul+ 2023 image is undersampled, this helps to suppress fluctuations in the image.",],
                           "Step 5a":["# Bool. Whether to track frame displacements by centroiding the 0th order.",],
                           "Step 5b":["# Bool. Whether to track frame displacements by centroiding background stars.",
                                      "# Lst of lst of float. Every list should indicate the estimated location of every background star",],
                           "Step 6":["# Bool. If True, saves the output xarray to be used in Stage 2.",],
                           }
    return header, subsection_headers, subsection_keys, subsection_comments