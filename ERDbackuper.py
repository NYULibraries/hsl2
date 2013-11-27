#! /usr/bin/python

import sys, os, subprocess, ConfigParser, time


cfg = ConfigParser.ConfigParser()
cfg.readfp(open(os.path.expanduser("~/cred.ini")))


dbname = 'mylibrary'
host     = cfg.get(dbname, 'host')
port     = cfg.get(dbname, 'port')
username = cfg.get(dbname, 'user')
password = cfg.get(dbname, 'pass')
query    = cfg.get(dbname, 'query')

git_dir  = os.path.expanduser('~/ERDdumps/hsl2')
ERDfile  = git_dir + '/ERDdata.txt'

timestamp = time.strftime("%c")



try:
    subprocess.check_call('mysql --skip-column-names -u %s -p"%s" -h %s -P %s %s -e "%s" > %s'
                            % (username, password, host, port, dbname, query, ERDfile),
                            shell=True)
except subprocess.CalledProcessError as e:
    print "\n\nMySQL Dump failed at %s with code: %s" % (timestamp, e.returncode)
    exit(1)
   

try:
    subprocess.check_call(['git','--git-dir', git_dir + '/.git',
                           '--work-tree', git_dir,
                           'add', ERDfile])
    subprocess.check_call(['git','--git-dir', git_dir + '/.git',
                           '--work-tree', git_dir,
                           'commit', '-m', 'ERD as of: ' + timestamp])
    subprocess.check_call(['git','--git-dir', git_dir + '/.git',
                           '--work-tree', git_dir,
                           'push', 'origin', 'master'])
except subprocess.CalledProcessError as e:
    print "\n\nGit push failed at %s with code: %s" %  (timestamp, e.returncode)
    exit(1)


print "ERD pushed to Github successfully at %s" % (timestamp)
exit(0)
