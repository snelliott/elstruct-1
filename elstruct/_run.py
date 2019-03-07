""" a simple helper command for running a given program
"""
import os
import stat
import tempfile
import subprocess
import warnings

SCRIPT_NAME = 'run.sh'
INPUT_NAME = 'input.dat'
OUTPUT_NAME = 'output.dat'


def new_run(script_str, input_writer,
            prog, method, basis, geom, mult, charge, **kwargs):
    """ run input file in a temporary directory using script

    (returns input string, output string, and temp run directory)
    """
    inp_str = input_writer(prog, method, basis, geom, mult, charge, **kwargs)
    out_str, tmp_path = run(script_str, inp_str, return_path=True)
    return inp_str, out_str, tmp_path


def run(script_str, input_str, return_path=False):
    """ run the program in a temporary directory and return the output
    """
    tmp_dir = tempfile.mkdtemp()

    with _EnterDirectory(tmp_dir):
        # write the submit script to the run directory
        with open(SCRIPT_NAME, 'w') as script_obj:
            script_obj.write(script_str)

        # make the script executable
        os.chmod(SCRIPT_NAME, mode=os.stat(SCRIPT_NAME).st_mode | stat.S_IEXEC)

        # write the input string to the run directory
        with open(INPUT_NAME, 'w') as input_obj:
            input_obj.write(input_str)

        # call the electronic structure program
        try:
            subprocess.check_call('./{:s}'.format(SCRIPT_NAME))
        except subprocess.CalledProcessError as err:
            # as long as the program wrote an output, continue with a warning
            if os.path.isfile(OUTPUT_NAME):
                warnings.warn("elstruct run failed in {}".format(tmp_dir))
            else:
                raise err

        # read the output string from the run directory
        assert os.path.isfile(OUTPUT_NAME)
        with open(OUTPUT_NAME, 'r') as output_obj:
            output_str = output_obj.read()

    return output_str if not return_path else (output_str, tmp_dir)


class _EnterDirectory():

    def __init__(self, directory):
        assert os.path.isdir(directory)
        self.directory = directory
        self.working_directory = os.getcwd()

    def __enter__(self):
        os.chdir(self.directory)

    def __exit__(self, _exc_type, _exc_value, _traceback):
        os.chdir(self.working_directory)
