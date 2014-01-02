from server import celery, db
import orm

import time

@celery.task()
def process_savfile(sav_id):
    percent_complete = 0

    while percent_complete <= 100:
        savfile_progress = orm.SAVFileProcessingProgress.query.filter_by(
            sav_id=sav_id).first()

        if savfile_progress is None:
            savfile_progress.status_message = "Can't find savfile with sav_id %s" % (
                sav_id)
            return

        savfile_progress.status_message = "Bumping savfile %s to %d%% complete" % (
            sav_id, percent_complete)
        savfile_progress.percent_complete = percent_complete

        db.session.add(savfile_progress)
        db.session.commit()

        percent_complete = (percent_complete + 10) % 90

        time.sleep(1)
