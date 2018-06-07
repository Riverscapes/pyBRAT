# -------------------------------------------------------------------------------
# Name:        Drainage_Area_Check
# Purpose:     Looks through the stream network for reaches that have lower drainage networks than reaches up stream of
#              them, and modifies the network to fix that
#
# Author:      Braden Anderson
#
# Created:     06/2018
# -------------------------------------------------------------------------------

from StreamObjects import DAValueCheckStream


def main(stream_network):
    """
    The main function
    :param stream_network: The stream network that we want to fix
    :return:
    """
    