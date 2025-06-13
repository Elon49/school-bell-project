import schedule
import time
import logging
import suno_script

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def job():
    logging.info('Running daily bell generation')
    suno_script.main()


def main():
    schedule.every().day.at('07:00').do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
