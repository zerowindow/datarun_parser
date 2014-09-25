#!/usr/bin/python
'''
Usage:
    parse_datarun.py HEXDATARUN
    
    HEXDATARUN is a hex formatted datarun.
    
    //This script has no support for input validation, it is up to you to validate
    //the correctness your datarun hex string. Run parse_datarun.py with no parameters
    //for an example and help syntax

Author: Matthew Seyer (research.forensics@gmail.com)
Purpose: Print human readable versions of an NTFS Hex formatted datarun

Datarun Examples and references:
http://www.reddragonfly.org/ntfs/concepts/data_runs.html
http://homepage.cs.uri.edu/~thenry/csc487/video/66_NTFS_Data_Runs.pdf
'''
import sys

class NtfsDatarun:
    def __init__(self,datarun_hex_str):
        '''Initialize the NtfsDatarun object with the given hex string datarun'''
        self.datarun_hex_str = datarun_hex_str
        # Parse our hex string datarun #
        self._ParseDataRun()
        
    def _ParseDataRun(self):
        '''Parse a hex string datarun [self.datarun_hex_str] and produce [self.datarun]:
            a cluseter string hex version,
            a cluseter string decimal version,
            a cluseter list
        '''
        self.datarun = {
            'cluster_hex_str' :'',
            'cluster_dec_str' :'',
            'cluster_list':''
        }
        
        self.datarun_bytes = [] # Byte List
        for i in range(0,len(self.datarun_hex_str),2):
            self.datarun_bytes.append(self.datarun_hex_str[i:i+2]) # Append each byte repersented by two hex characters
        
        byte_list = self.datarun_bytes # create copy of datarun_bytes to pop from
        
        byte_value = byte_list.pop(0) #grab first byte in array
        
        counter = 1
        current_cluster = 0
        
        while (byte_value != '00'):
            ##this data run dictionary###
            this_datarun = {
                'ln' : int(byte_value[0:1], base=16),#left nible value
                'rn' : int(byte_value[1:2], base=16),#right nible value
                'contig_cnt' : 0, #number of contiguous clusters
                'cluster' : 0 #cluster (start clust if 1st run, else offset to next clusters)
            };
            
            ###get length###
            this_datarun['len'] = this_datarun['ln'] + this_datarun['rn']
            
            ##get number of contigous clusters###
            contig_str = ''
            for a in range(0,this_datarun['rn']):
                hex_value = byte_list.pop(0)
                contig_str = hex_value + contig_str;
            
            int1 = int(contig_str, base=16) #contigous cluster string to intiger
            this_datarun['contig_cnt'] = int1
            this_datarun['contig_cnt_h'] = hex(int1)
            
            ##get starting cluster###
            start_str = ''
            for a in range(0,this_datarun['ln']):
                hex_value = byte_list.pop(0)
                start_str = start_str + hex_value
                
            int2 = 0
            
            ###Get Signed value of start_str###
            int2 = int(start_str, base=16)
            
            ofs = hex(int2)
            
            if counter > 1 and this_datarun['ln'] > 0:
                int2 = int2 + current_cluster
            
            this_datarun['cluseter'] = int2
            this_datarun['cluseter_h'] = hex(int2)
            
            ###Do not set the clust to 0###
            if this_datarun['cluseter'] != 0:
                current_cluster = this_datarun['cluseter']
            
            # Concat our cluster hex string #
            self.datarun['cluster_hex_str'] += '{0:s},{1:s}(ofs: {2:s});'.format(
                this_datarun['cluseter_h'],
                this_datarun['contig_cnt_h'],
                ofs
            )
            
            # Concat our cluster decimal string #
            self.datarun['cluster_dec_str'] += '{0:d},{1:d};'.format(
                this_datarun['cluseter'],
                this_datarun['contig_cnt']
            )
            
            if this_datarun['cluseter'] != 0:
                # Create cluster list #
                for a in range(0,this_datarun['contig_cnt']):
                    self.datarun['cluster_list'] += '{0:d},'.format(
                        (this_datarun['cluseter'] + a)
                    )
            
            byte_value = byte_list.pop(0) #grab byte in array
            
            counter += 1

    def PrintClusterList(self):
        print "Cluseter List:"
        print self.datarun['cluster_list']
        print "-----------------------------------------------"
        
    def PrintDecClusterStr(self):
        print "Cluseter String (Decimal):"
        print self.datarun['cluster_dec_str']
        print "-----------------------------------------------"
        
    def PrintHexClusterStr(self):
        print "Cluseter String (Hex):"
        print self.datarun['cluster_hex_str']
        print "-----------------------------------------------"
        
    def PrintAll(self):
        self.PrintClusterList()
        self.PrintDecClusterStr()
        self.PrintHexClusterStr()
        
# Get our first arguement #
# example: 3138732534321401E511023142AA000300
datarun_hex_str = ''

if len(sys.argv) > 1:
    datarun_hex_str = sys.argv[1]
else:
    print "Usage:"
    print "  parse_datarun.py HEXDATARUN"
    print "Example:"
    print "  parse_datarun.py 3138732534321401E511023142AA000300"
    sys.exit(-1)

dataRunObj = NtfsDatarun(datarun_hex_str)
dataRunObj.PrintAll()

print 'end'