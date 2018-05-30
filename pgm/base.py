import inspect


class PGM(object):
    """
    Base class for any module in coremods which gets called by the shake
    program.
    """

    def __init__(self):
        self._units = ''

    def getPGM(self, stream, **kwargs):
        """ Return the peak ground motion for the child class IMT.

        Args:
            stream (Obspy Stream): Stream object containing one or more Traces.
            kwargs (**args): Keyword arguments which may be required by PGM.
                instances.
        Returns:
            dict: Dictionary containing peak ground motion for each channel:
                  {'H1':1.0,'H2':1.5,'Z':1.8}.
        """
        raise NotImplementedError('Instantiate a child class first.')

    def getUnits(self):
        """Return the units associated with the PGM.

        Returns:
            str: String units (cm/sec, m/s^2, etc.)
        """
        return self._units

    def parseArgs(self, arglist):
        """Parse command line arguments.

        This is the default parseArgs which is sufficient for most
        modules. It will respond to '-h' or '--help' but nothing
        else. If a module needs to accept command line arguments,
        it will need to override this module.

        Args:
            arglist (list): List of potential command line arguments.
        Returns:
            list: Arguments not parsed.
        """
        cmd_name = __name__  # this should be the name of the module
        doc_str = inspect.getdoc(self.__class__)
        parser = argparse.ArgumentParser(prog=cmd_name,
                                         description=doc_str)
        #
        # This line should be in any modules that overrides this
        # one. It will collect up everything after the current
        # modules options in args.rem, which should be returned
        # by this function. Note: doing parser.parse_known_args()
        # will not work as it will suck up any later modules'
        # options that are the same as this one's.
        #
        parser.add_argument('rem', nargs=argparse.REMAINDER,
                            help=argparse.SUPPRESS)
        args = parser.parse_args(arglist)
        return args.rem
