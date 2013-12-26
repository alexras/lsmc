from server import celery, db
import orm

import time

@celery.task()
def process_savfile(uuid):
    percent_complete = 0

    while percent_complete <= 100:
        savfile = orm.SAVFile.query.filter_by(uuid=uuid).first()

        if savfile is None:
            print "Can't find savfile with uuid %s" % (uuid)
            return

        print "Bumping savfile %s to %d%% complete" % (uuid, percent_complete)
        savfile.percent_complete = percent_complete

        db.session.add(savfile)
        db.session.commit()

        percent_complete = (percent_complete + 10) % 90

        time.sleep(1)
