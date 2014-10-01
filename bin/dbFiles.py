from optparse import OptionParser  
import os

parser = OptionParser(usage = 'bla', version = '0.1')

parser.add_option("-f", "--file", dest="file", 
	help="File containing the certs/csr which should be seperated.", metavar="FILE")
	
parser.add_option("-d", "--destination", dest="dest", 
	help="Destination folder", metavar="FILE")
parser.add_option("-c", "--cert", action='store_true', default=False, dest="cert", 
	help="Contains the file Certificates", metavar="FILE")

options, args = parser.parse_args()

f = open(options.file)
lines = f.read().split('\n')

start=0
fileNo=0
end_found=False

for end in range(0, len(lines)):
	if options.cert and '----END CERTIFICATE----' in lines[end]:
		end_found = True
		lines[end]='-----END CERTIFICATE-----'
	if not options.cert and '----END NEW CERTIFICATE REQUEST----' in lines[end]:
		end_found = True
		lines[end]='-----END NEW CERTIFICATE REQUEST-----'
	if not options.cert and '----END CERTIFICATE REQUEST----' in lines[end]:
		end_found = True
		lines[end]='-----END CERTIFICATE REQUEST-----'
		
	if end_found:
		k=end-1
		while k>= start:
			if options.cert and '----BEGIN CERTIFICATE----' in lines[k]:
				lines[k]='-----BEGIN CERTIFICATE-----'
				break
			if not options.cert and '----BEGIN NEW CERTIFICATE REQUEST----' in lines[k]:
				lines[k]='-----BEGIN NEW CERTIFICATE REQUEST-----'
				break				
			if not options.cert and '----BEGIN CERTIFICATE REQUEST----' in lines[k]:
				lines[k]='-----BEGIN CERTIFICATE REQUEST-----'
				break
			k-=1
		
		if k<start:
			print start, end, k
			print '\n'.join(lines[end-20:end+1])
			raise Exception('k zu klein')
		
		if end-k>100:
			print start, end, k
			print '\n'.join(lines[end-20:end+1])
			raise Exception('Datei erscheint zu lang')
		
		s = '\n'.join([l for l in lines[k:end+1] if l.strip()])
		
		
		writefile = open(options.dest+str(fileNo), 'w')
		writefile.write(s)
		writefile.close()
		
		fileNo+=1
		start=end+1
		end_found=False
		