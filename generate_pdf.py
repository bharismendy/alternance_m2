import subprocess
import os
import sys
import getopt
import shutil
from md2pdf.core import md2pdf


def generate_pdf(path):
    # this function list all markdown file and generate the pdf file
    # param path = path to the target directory

    destination_dir = "pdf"
    if os.path.isdir(os.path.join(path, destination_dir)):
        shutil.rmtree(os.path.join(path, destination_dir))
    os.mkdir(os.path.join(path, destination_dir))
    p2 = None
    list_of_process = []
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".md")]:
            if not filename == 'README.md':
                print("start " + filename)
                with open(os.path.join(path, destination_dir, filename + ".pdf"), 'w+') as output:
                    p1 = subprocess.Popen(["markdown", os.path.join(dirpath, filename)], encoding="utf-8",
                                          stdout=subprocess.PIPE)  # first part of the command
                    p2 = subprocess.Popen(["htmldoc", "--cont", "--headfootsize", "8.0", "--linkcolor", "blue",
                                           "--linkstyle", "plain", "--charset", "utf-8", "--format", "pdf14", "-"],
                                          encoding="utf-8",
                                          stdin=p1.stdout, stdout=output)  # second part of the command
                    p1.stdout.close()  # set free the first process
                    list_of_process.append(p2)
                    output.flush()  # flush the output file
    for p in list_of_process:
        p.wait()
    print("the work is done")

    """
    
    destination_dir = "pdf2"
    if os.path.isdir(os.path.join(path, destination_dir)):
        shutil.rmtree(os.path.join(path, destination_dir))
    os.mkdir(os.path.join(path, destination_dir))
    for dirpath, dirnames, filenames in os.walk("."):
        for filename in [f for f in filenames if f.endswith(".md")]:
            if not filename == 'README.md':
                print("start " + filename)
                md2pdf(os.path.join(path, destination_dir, filename + ".pdf"), md_content=None, md_file_path=os.path.join(dirpath, filename))
    """

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hp:", ["path"])
    except getopt.GetoptError:
        print('python generate_pdf.py -p <path_to_directory>')
        sys.exit(2)
    path_to_file = ''
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('python generate_pdf.py -p <path_to_directory>')
            sys.exit()
        elif opt in ("-p", "--path"):
            path_to_file = arg
    if not opts:
        print('python generate_pdf.py -h to see how its works')
        exit(2)
    generate_pdf(path=path_to_file)


if __name__ == '__main__':
    main(sys.argv[1:])
