#! /usr/bin/python3
from datetime import datetime, timedelta, date
import gzip
import os
import sys, getopt
from setting import DATA_DIR, PREFIX_FILE, SUFFIX_COMPRESS


def check_line(line_to_test,search):
    """
    param line_to_test : line of the file to test
    param search : the string to find
    return : boolean
    """
    if type(search) is str:
        if search.casefold() in line_to_test.casefold():
            return True
        else:
            return False
    else:
        for element in search :
            if not element.casefold() in line_to_test.casefold():
                return False
        return True

def get_line_time(time_start, time_stop, line_to_test):
    """return tab of line"""
    tab_of_line = []
    line_to_test.strip()
    date_of_line = datetime.strptime(line_to_test.split()[2],"%H:%M:%S")
    if time_start<=date_of_line<=time_stop:
        return True
    else:
        return False

def find_time_in_file(file, time_start, time_stop):
    tab_of_line = []
    for line in file:
        if not type(line) is str:
            line = line.decode("utf-8")
        if '\n' in line:
            line = line.replace("\n","")
        if get_line_time(line_to_test = str(line), time_start = time_start, time_stop = time_stop):
            tab_of_line.append(line)
    return list(filter(None,tab_of_line))

def find_string_in_file(search, file = None, tab_of_line = None):
    result_line = []
    if file :
        for line in file:
            if not type(line) is str:
                line = line.decode("utf-8")
            if '\n' in line:
                line = line.replace("\n","")
            if check_line(str(line),search):
                result_line.append(str(line))
    elif tab_of_line :
        for line in tab_of_line:
            if not type(line) is str:
                line = line.decode("utf-8")
            if '\n' in line:
                line = line.replace("\n","")
            if check_line(str(line),search):
                result_line.append(str(line))
    return list(filter(None,result_line))

def flatten_array(to_flatten):
    if isinstance(to_flatten, list):
        if len(to_flatten) == 0:
            return []
        first, rest = to_flatten[0], to_flatten[1:]
        return flatten_array(first) + flatten_array(rest)
    else:
        return [to_flatten]

def launch_search(file_open, search = None, time_start = None, time_stop = None):
    result_line = []
    if time_start and time_stop and search:
        tab_of_line = find_time_in_file(file = file_open, time_start = time_start, time_stop = time_stop)
        result_line.append(find_string_in_file(tab_of_line = tab_of_line, search = search))
    elif search :
        result_line.append(find_string_in_file(file = file_open, search = search))
    elif time_stop and time_start :
        result_line.append(find_time_in_file(file = file_open, time_start = time_start, time_stop = time_stop))
    else :
        raise Exception("error: you must specify search argument")
    return result_line

def search_in_file(code_college, search = None, time_start = None, time_stop = None, date_spe = None, api=False):
    sys.setrecursionlimit(150000)
    result = []
    path_to_dir = os.path.join(DATA_DIR, code_college)
    if not code_college:
        raise Exception("You must specify a college code")
    if time_start and time_stop:
        time_start = datetime.strptime(time_start,"%H:%M:%S")
        time_stop = datetime.strptime(time_stop, "%H:%M:%S")
        if time_stop<time_start:
            raise Exception("error the starting time must be greater that the stop one")
    if date_spe:
        # date_spe format DD/MM/YYYY
        temp_date = date_spe
        date_spe = date_spe.split("/")
        if not len(date_spe) == 3:
            raise Exception("Enter a properly formated date (DD/MM/YYYY)")
        date_spe_previous_datetime = datetime.strptime(temp_date, "%d/%m/%Y")-timedelta(1)
        date_spe_previous = [0,0,0]
        date_spe_previous[0] = str(date_spe_previous_datetime.day).zfill(2)
        date_spe_previous[1] = str(date_spe_previous_datetime.month).zfill(2)
        date_spe_previous[2] = str(date_spe_previous_datetime.year).zfill(4)

        if len(date_spe[0 or 1])<2: # cheking if the month or the day have the right size
            date_spe[0].zfill(2)
            date_spe[1].zfill(2)
        if len(date_spe[2])<4: # we check if the date is properly formated
            date_spe[2].zfill(4)

        if not datetime.strptime(temp_date,"%d/%m/%Y") == date.today():
            filename = PREFIX_FILE+date_spe[2]+date_spe[1]+date_spe[0]+".gz"
            with gzip.open(os.path.join(path_to_dir,filename), mode='rb', compresslevel=9) as file_open:
                result.append(launch_search(file_open = file_open, search = search, time_start = time_start, time_stop = time_stop))
        else:
            filename = PREFIX_FILE.replace("-","")
            with open(os.path.join(path_to_dir,filename), mode='r') as file_open:
                result.append(launch_search(file_open = file_open, search = search, time_start = time_start, time_stop = time_stop))

        # we check the previous day
        filename = PREFIX_FILE+date_spe_previous[2]+date_spe_previous[1]+date_spe_previous[0]+SUFFIX_COMPRESS
        with gzip.open(os.path.join(path_to_dir,filename), mode='rb', compresslevel=9) as file_open:
            result.append(launch_search(file_open = file_open, search = search, time_start = time_start, time_stop = time_stop))
    else:
        for file in os.listdir(path_to_dir):
            if file.startswith('dcauth'):
                if file.endswith(".gz"):
                    with gzip.open(os.path.join(path_to_dir,file), mode='rb', compresslevel=9) as file_open:
                        result.append(launch_search(file_open = file_open, search = search, time_start = time_start, time_stop = time_stop))
                else:
                    with open(os.path.join(path_to_dir,file), mode='r') as file_open:
                        result.append(launch_search(file_open = file_open, search = search, time_start = time_start, time_stop = time_stop))
        result =list(filter(None, result))

    # flatten the result array
    result = flatten_array(result)
    if not api:
        if result:
            for element in result:
                print(element)
        else:
            print("no result found")
    else:
        return result

if __name__ == "__main__":
    code_college = None
    time_start = None
    time_stop = None
    search = None
    date_spe = None
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"hc:s:t:T:d:",["code_college=","time_start=", "time_stop=", "search=", "date_spe=","help"])
    except getopt.GetoptError as error:
        print("you must specify a code of a college")
        print('find usage with -h option')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h','--help'):
            print("man of the command")
            print("-h or --help -> access to how to use the command")
            print("-c --code_college -> The NRE of the college")
            print("-s --search -> your research")
            print("-t --time_start -> the lower band of your research, the format is HH:MM:SS")
            print("-T --time_stop -> the lower band of your research, the format is HH:MM:SS")
            print("-d or --date_spe -> a specific day to look for, the format is DD/MM/YYYY")
            sys.exit()
        elif opt in ("-c", "--code_college"):
            code_college = arg
        elif opt in ("-s", "--search"):
            search = arg
        elif opt in ("-t", "--code_college"):
            time_start = arg
        elif opt in ("-T", "--code_college"):
            time_stop = arg
        elif opt in ("-d", "--code_college"):
            date_spe = arg
    if not code_college:
        print("you must at least specify a code of a college")
        print('find usage with -h option')
        sys.exit()
    search_in_file(code_college=code_college,time_start=time_start, time_stop=time_stop, search=search, date_spe=date_spe)
