#!/usr/bin/python


import sys
from optparse import OptionParser
import logging
import os
import platform
import datetime
import time
import yaml
import math
from cgi import log

# Optimal INOL values per exercise for a single workout:
# 
# < 0.4 - too easy
# 0.4 - 1.0 - optimal range for most athletes. An INOL value between 0.7 - 0.8 is a recommended starting point.
# 1.0 - 2.0 - tough workout, but good occasionally, especially for loading phases
# > 2.0 - very difficult and could lead to overtraining if performed regularly in most individuals
# Optimal INOL values per exercise across an entire week:
# 
# 2.0 - easy, good for reloading, could probably benefit from greater volume occasionally
# 2.0 - 3.0 - tougher, but doable, good for loading phases
# 3.0 - 4.0 - very tough, good for shocking your body, but not recommended for extended periods of time
# > 4.0 - not recommended


#current_max = 140



#max_exercise_inol = 2
#min_exercise_inol = 0.4
#max_set_inol = 0.5
#min_set_inol = 0.05

#intensity_increment = 5
#max_intensity = 95

#target_exercise_inol = 0.6

def generate_training_options(current_max, max_reps, intensity, min_sets, max_sets, min_set_inol, max_set_inol, min_exercise_inol, max_exercise_inol):
    training_options = []
    for r in range(1, max_reps + 1):
        logging.debug("using reps {0}".format(str(r)))
        set_inol = calculate_set_inol(r, intensity)
        logging.debug("set inol for {0} rep(s) @ {1} is {2}".format(str(r), str(intensity), str(set_inol)))
        for s in range(min_sets, max_sets + 1):
            exercise_inol = set_inol * s
            volume = r * s
            weight = current_max * (float(intensity)/100)
            weight_powerlifting = roundPowerlifting(weight)
            weight_olympic = roundOlympiclifting(weight)
            scheme = str(s) + "x" + str(r) + "@" + str(intensity) + "%"
            if set_inol > min_set_inol:
                if set_inol < max_set_inol:
                    if exercise_inol > min_exercise_inol:
                        if exercise_inol < max_exercise_inol:
                            training_options.append(
                                {
                                    "scheme":scheme, 
                                    "exercise_inol":exercise_inol, 
                                    "set_inol":str(set_inol), 
                                    "volume":str(volume),
                                    "weight": str(weight),
                                    "weight_powerlifting": str(weight_powerlifting),
                                    "weight_olympic": str(weight_olympic)
                                    })
    
    return training_options

def main():
    
    start = time.time()
   
    this = os.path.splitext(os.path.basename(__file__))[0]
    whereami = os.path.dirname(__file__)
    
    this_platform = platform.system()
    log_location = "/var/tmp"
    
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    if this_platform == "Windows":
        log_location = "C:\\" + log_location
    
    if whereami == ".":
        whereami = os.getcwd()
    
    
    
    parser = OptionParser()
    #parser.add_option("--intensity",  type=int, default="80", help="% intensity")
    #parser.add_option("--inol",  type=float, default="0.8", help="target exercise inol")
    #parser.add_option("--max",  type=int, default="10", help="max reps")
    #parser.add_option("--sets",  type=int, default="10", help="max sets")
    parser.add_option("--weeks",  type=int, default="6", help="training weeks")
    parser.add_option("--verbose",action="store_true", dest="verbose", help="turn on verbose output")
    parser.add_option("--output", help="where to write the versions")
    parser.add_option("--config", help="config file to use in yaml format")
    

    (options, args) = parser.parse_args()
    
    if options.verbose:
        print "verbose enabled"
 
    #if not options.intensity:
    #    parser.error("intensity is required")
    
    if not options.output:
        parser.error("output is required")
    
    if not options.config:
        parser.error("config is required")
             
    setupLogging(log_location, this, now, options.verbose)

    if os.path.isfile(options.config):
        logging.debug("found config file {0}".format(options.config))
    else:    
        logging.error("{0} does not exist".format(options.config))
        os.sys.exit(99)
    


    logging.info("bootstrap info")
    

    logging.info('this=' + this)
    #logging.info("PLATFORM: " + this_platform)
    #logging.info('INTENSITY=' +  str(options.intensity))
    #logging.info('MAX=' +  str(options.max))
    #logging.info('SETS=' +  str(options.sets))
    #logging.info('WEEKS=' +  str(options.weeks))
    #logging.info('OUTPUT_DIR=' +options.output)


    if not ensureDir(options.output):
        logging.fatal("{0} does not exist and could not be created".format(options.output))
        sys.exit(94)

    config = []

    with open(options.config, 'r') as config_file:
        config = yaml.load(config_file)

    logging.debug(config)
    logging.info("name: " + config["name"])
    logging.info("target_exercise_inol: " + str(config["target_exercise_inol"]))  
    logging.info("min_set_inol: " + str(config["min_set_inol"]))
    logging.info("current_max: " + str(config["current_max"]))
    logging.info("max_exercise_inol: " + str(config["max_exercise_inol"]))
    logging.info("max_set_inol: " + str(config["max_set_inol"]))
    logging.info("min_set_inol: " + str(config["min_set_inol"]))
    logging.info("intensity_increment: " + str(config["intensity_increment"]))
    logging.info("max_intensity: " + str(config["max_intensity"]))        
    logging.info("max_reps: " + str(config["max_reps"]))   
    logging.info("min_sets: " + str(config["min_sets"]))   
    logging.info("min_reps: " + str(config["min_reps"]))
    if 'training_day' in config:
        logging.info("training_day" +  str(config["training_day"]))  

    min_intensity = config["max_intensity"] - (config["intensity_increment"] * options.weeks)
    logging.info("min_intensity: {0}".format(str(min_intensity)))
    
    training_plan_file_name = "training_plan_" + str(config["max_reps"]) + "_" + str(config["max_sets"]) + "_" + str(options.weeks) + "_" + str(config["target_exercise_inol"])
    training_plan_file_path = options.output + "/" + training_plan_file_name + ".yaml"
    
    #training_plan_summary_file_name = "training_plan_summary_" + str(config["max_reps"]) + "_" + str(config["max_sets"]) + "_" + str(options.weeks) + "_" + str(config["target_exercise_inol"])
    training_plan_summary_file_name = "README"   #This makes it show up nice in git
    training_plan_summary_file_path = options.output + "/" + training_plan_summary_file_name + ".md"          
            
    training_plan = []             
    week = 0
    while (week < options.weeks + 1):
        intensity = min_intensity + (week * config["intensity_increment"] )
        week = week + 1
        logging.info("Generating training optios for intensity {0} in week {1}".format(str(intensity),str(week)))
        
        #current_max, max_reps, intensity, min_sets, max_sets, min_set_inol, max_set_inol, min_exercise_inol, max_exercise_inol
        training_options = generate_training_options(config["current_max"], config["max_reps"], intensity, config["min_sets"], config["max_sets"], config["min_set_inol"], config["max_set_inol"], config["min_exercise_inol"], config["max_exercise_inol"])
    
         #sorted_training_options = sorted(training_options, key=lambda k: k['exercise_inol'])
        sorted_training_options = sorted(training_options, key=lambda k: (k['exercise_inol'],k['set_inol'],k['volume'] ))
        #print sorted_versions
        logging.debug("\n" +yaml.dump(sorted_training_options, default_flow_style=False))
    
        output_file_name = "training_options_" + str(intensity) + "_" + str(config["max_reps"]) + "_" + str(config["max_sets"])
  
        output_file_path = options.output + "/" + output_file_name + ".yaml"
    
        with open(output_file_path, 'w') as outfile:
            yaml.dump(sorted_training_options, outfile, default_flow_style=False)
        
        #We pick a training option 
        best_training_option = None
        for training_option in training_options:
            
            #print training_option['exercise_inol']
            
            if best_training_option is None:
                best_training_option = training_option
            else:
                #print training_option
                #print best_training_option
                best_difference = getInolDifference(config["target_exercise_inol"], best_training_option['exercise_inol']);
                training_option_difference = getInolDifference(config["target_exercise_inol"], training_option['exercise_inol']);
                
                if training_option_difference < best_difference:
                    logging.info("Option {2} is better {1} < {0}: ".format(str(best_difference),str(training_option_difference),str(training_option['scheme'])))
                    best_training_option = training_option
                else:
                    logging.info("Option {2} is worse {1} > {0}: ".format(str(best_difference),str(training_option_difference),str(training_option['scheme'])))
                
            
        logging.info("found best training {0} option for week {1}s".format(str(best_training_option),str(week)))
        
        best_training_option["week"] = week
        training_plan.append(best_training_option)


    sorted_training_plan = sorted(training_plan, key=lambda k: (k['week']))
    with open(training_plan_file_path, 'w') as outfile:
            yaml.dump(sorted_training_plan, outfile, default_flow_style=False)
            
    with open(training_plan_summary_file_path, 'w') as outfile2:
        
        #Markdown | Less | Pretty
        #--- | --- | ---
        #*Still* | `renders` | **nicely**
        #1 | 2 | 3
        
        
        #name: snatch
        #current_max: 125
        #target_exercise_inol: 0.8
        #max_exercise_inol: 2
        #min_exercise_inol: 0.3
        #max_set_inol: 0.5
        #min_set_inol: 0.05
        #intensity_increment: 5
        #max_intensity: 95
        #max_reps: 5
        #min_reps: 1
        #min_sets: 1
        #max_sets: 10
        
        
        header1 = "## {0}\n\n".format(config["name"].title())
        if 'training_day' in config:
            header1 = "## {0} ({1})\n\n".format(config["name"].title(),config["training_day"].title())
        outfile2.write(header1)
        
        header2 = "### {0}\n\n".format("Summary")
        outfile2.write(header2)
        
        header_table_headers = "{0} | {1} | {2} | {3} | {4}\n".format("Weeks","Max","Target INOL","Max Reps","Max Sets")
        outfile2.write(header_table_headers)
        
        header_table_def = "--- | --- | --- | --- | ---\n"
        outfile2.write(header_table_def)
        
        header_table_data = "{0} | {1} | {2} | {3} | {4}\n\n".format(str(options.weeks),config["current_max"],config["target_exercise_inol"],config["max_reps"],config["max_sets"])
        outfile2.write(header_table_data)
        
        
        header3 = "#### {0}\n\n".format("Plan")
        outfile2.write(header3)
        #header = "{0:5} {1:12} {2:8} {3:10} {4:8}\n".format("Week","Scheme","Weight","Olympic", "Power")
        
        data_table_headers = " ... | {0} | {1} | {2} | {3}\n".format("Sets/Reps","Weight","Olympic","Power")
        outfile2.write(data_table_headers)
        
        data_table_def = "--- | --- | --- | --- | ---\n"
        outfile2.write(data_table_def)
        
        #seperator = "{0:_<10}\n".format("#")
        #outfile2.write(header)
        #outfile2.write(seperator)
        for week in sorted_training_plan:
            #summary = "{0:5} {1:12} {2:8} {3:10} {4:8}\n".format(str(week['week']),week['scheme'],week['weight'],week['weight_olympic'],week['weight_powerlifting'])
            summary = "{0} | {1} | {2} | {3} | {4}\n".format(str(week['week']),week['scheme'],week['weight'],week['weight_olympic'],week['weight_powerlifting'])
            outfile2.write(summary)
        outfile2.write("\n")
        
        if 'notes' in config:
            header4 = "### {0}\n\n".format("Notes")
            outfile2.write(header4)
            for note in config["notes"]:
                note_item = "- {0}\n".format(note)
                outfile2.write(note_item)
            outfile2.write("\n")
    #end = time.time()
    #elapse = end - start

    #logging.info("found {0} training option(s) in {1}s".format(str(len(sorted_training_options)),str(elapse)))
    
def getInolDifference(target_exercise_inol,exercise_inol):
    return math.fabs(target_exercise_inol - exercise_inol)
    
def roundPowerlifting(x, precision=1, base=2.5):
    return round(base * round(float(x)/base),precision)

def roundOlympiclifting(x, precision=0, base=1):
    return round(base * round(float(x)/base),precision)    
    
def calculate_set_inol(reps, intensity):
    return float(reps) / (100 - intensity)

def ensureDir(path):
    
    if os.path.isdir(path):
        logging.debug("{0} exists and is a directory".format(path))
        return True
    
    try:
        logging.debug("making " + path) 
        os.makedirs(path)
        return True
    except Exception as e:
        if not os.path.isdir(path):
            logging.error("Could not make " + path + " {0}): {1} ".format(e.errno, e.strerror)) 
            raise
  
def setupLogging(log_location, this, now, verbose):

    
        # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.INFO,
                    #format='%(asctime)s %(name)-12s %(levelname)-8s (%(threadName)-10s) %(message)s',
                    format='%(asctime)s %(levelname)-8s (%(threadName)-10s) %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=log_location + '/' + this.upper() + "_" + now +'.txt',
                    filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    if verbose:
        console.setLevel(logging.DEBUG)
        
  
        
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(levelname)-8s (%(threadName)-10s) %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...
    logging.debug('logging initialised')
    
    logging.debug("debug is on")

if __name__ == '__main__':
 main()