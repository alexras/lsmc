test:
	  cd tests
		pypy -m nose .

profile:
		cd tests
		nosetests --with-cprofile --cprofile-stats-file=profiler.out .
