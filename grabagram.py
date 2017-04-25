''' uses Firefox to archive images from your Instagram feed, also archives
the meta data associated with each image in a CSV'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from random import randint
import lxml.html
import time
import csv
import urllib
import os


class Gramatron():

    def __init__(self):
        # profiles allow the browser preferences to be set as selenium
        # normally starts an unconfigured browser each time
        profile = webdriver.FirefoxProfile()
        # turn off image loading for speed and sneakiness
        profile.set_preference('permissions.default.image', 2)
        self.driver = webdriver.Firefox(profile)
        # implicit wait is the time that all the 'wait.untils' will wait
        self.driver.implicitly_wait(30)
        #  don't stop for silliness
        self.verificationErrors = []
        self.accept_next_alert = True
        self.default = 'None'

    def start(self):
        driver = self.driver
        default = self.default
        tag = 'cheatmeal'  # the tag you want to get

        # the attack begins, load the tag page and wait for a few seconds
        driver.get("https://www.instagram.com/explore/tags/" + tag)
        driver.wait = WebDriverWait(driver, 3)

        ''' from here on we are dependent on the CSS structure of the page,
        which will get changed by instagram at some stage and break our code,
        this try/except structure will ensure that you get some idea that this
        has happened by printing an error message if can't find an element
        thats meant to be there this can also be triggered by a very slow
        connection or you're connection being lost '''
        try:
            # wait for the 'load more' button to appear on the page
            # so we can click it
            driver.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Load more")))
            driver.find_element_by_link_text("Load more").click()

            # make a directory to store this tags images in
            out_folder = os.getcwd() + "/images/" + tag
            if not os.path.exists(out_folder):
                os.makedirs(out_folder)

            # open a new csv for the tag to store the metadata
            csvfile = open(out_folder + '_meta.csv', 'w')
            csvwriter = csv.writer(csvfile)

            # sneaky, makinf it look this code is really a Firefox browser
            urllib.URLopener.version = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:47.0) Gecko/20100101 Firefox/47.0'

            # fake scrolling down the page a long, long way
            for i in range(1, 3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(randint(9, 11))

            # now we have a really, really long page in the zombied browser,
            # lets get the HTML an pull it apart to get at the images and data
            dom_tree = lxml.html.fromstring(driver.page_source)
            anchors = dom_tree.cssselect('a._8mlbc._vbtk2._t5r8b')
            for anchor in anchors:
                url = anchor.attrib['href']
                # reduce the wait time as this can be used to handle the
                # error page logic as well
                driver.implicitly_wait(randint(3, 5))
                driver.get('https://www.instagram.com' + url)
                # sometimes a gram that was on the index gets deleted and
                # the page errors
                try:
                    error = driver.find_element_by_tag_name('h2')
                    print 'NOTICE: http://www.instagram.com' + url
                    + ' - cannot be found (deleted, private)'
                except NoSuchElementException:
                    timestamp = driver.wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "._379kp")))
                    dom_tree = lxml.html.fromstring(driver.page_source)

                    # we can now start to extract data from the page
                    # there is always a timestamp & username so we don't need to handle empties
                    timestamp = dom_tree.cssselect('._379kp')[0].get('datetime', default)
                    username = dom_tree.cssselect('a._4zhc5.notranslate._ook48')[0].text.encode('utf-8')

                    # place, likes and descriptions are optional so we need to
                    # handle empty ones
                    try:
                        place = dom_tree.cssselect('a._kul9p._rnlnu')[0].get('title',default).encode('utf-8')
                    except IndexError:
                        place = default
                    try:
                        likes = dom_tree.cssselect('span._tf9x3 > span')[0].text
                        # TODO need to convert K likes to numbers
                    except IndexError:
                        likes = '0'
                    try:
                        description = dom_tree.cssselect('li._nk46a > h1 > span')[0].text_content()
                    except IndexError:
                        description = default

                    # sometimes there is no image in the gram but a video instead...
                    try:
                        image = dom_tree.cssselect('._icyx7')[0].attrib['src']
                    except IndexError:
                        image = dom_tree.cssselect('video')[0].attrib['src']

                    # download the image using the grams own filename
                    filename = image.split("/")[-1]
                    filename = filename.split("?")[0] # remove the caching number
                    outpath = os.path.join(out_folder, filename)
                    urllib.urlretrieve(image, outpath)

                    # write the meta data out to the CSV file, note the description can have non ASCII chars
                    csvwriter.writerow([timestamp, username, place, description.encode('utf-8'), likes, filename])
                    csvfile.flush()

                    # give some feedback on the console
                    print(timestamp, username, place, description.encode('utf-8'), likes, filename)

                    #  I can haz fotos? (another small wait after the image download)
                    time.sleep(randint(3,5))

        except TimeoutException:
            # this will be triggered if they change th classes in then UI
            print("Page element not found in Instagram.com or the site is currently unreachable")

        print "FINISHED"
        driver.quit()
        csvfile.close()


if __name__ == "__main__":
    scrape = Gramatron()
    scrape.start()
