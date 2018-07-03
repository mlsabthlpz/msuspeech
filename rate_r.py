# MSU Perceptual Ratings
# Author: Melissa Lopez

import pymysql.cursors
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

# create app and db
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = '****'

connection = pymysql.connect(host='****',
                             user='****',
                             password='****',
                             db='speechratings',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
dump = 0

def denyiphone():
    '''Deny iPhone users access to page.'''
    if request.user_agent.platform == 'iphone':
        return redirect(url_for('deny'))

@app.route('/')
def index():
    if request.user_agent.platform == 'iphone':
        return redirect(url_for('deny'))
    else:
        return render_template('login.html')
    
@app.route('/deny')
def deny():
    return render_template('deny.html')

@app.route('/menu')
def menu():
    with connection.cursor() as cursor:
        startpoint = "SELECT `trainingnum` FROM `users` WHERE `userid`=%s"
        cursor.execute(startpoint, (session['username'],))
        trainingnum = cursor.fetchone().get('trainingnum')
        if trainingnum < 24 and trainingnum > 0:
            flash("You must complete the training set to access the menu.")
            return redirect(url_for('training'))
        else:
            getpractscore = "SELECT `trainingtotal` FROM `users` WHERE `userid`=%s"
            cursor.execute(getpractscore, (session['username'],))
            trainingtotal = cursor.fetchone().get('trainingtotal')
            practicescore = (trainingtotal * 100) / 24
            gettestscore = "SELECT `testtotal` FROM `users` WHERE `userid`=%s"
            cursor.execute(gettestscore, (session['username'],))
            testtotal = cursor.fetchone().get('testtotal')
            testscore = testtotal
            return render_template('menu.html', practicescore=str(practicescore), testscore = str(testscore))
 
@app.route('/ineligiblescore')
def ineligiblescore():
    return render_template('ineligible.html')

@app.route('/rate/<dumpnum>', methods = ['GET'])
def page(dumpnum):
    if request.user_agent.platform == 'iphone':
        return redirect(url_for('deny'))
    else:
        dump = dumpnum
        with connection.cursor() as cursor:
            gettestscore = "SELECT `testtotal` FROM `users` WHERE `userid`=%s"
            cursor.execute(gettestscore, (session['username'],))
            testtotal = cursor.fetchone().get('testtotal')
            totalcount = "SELECT `itemnum` FROM `users` WHERE `userid`=%s"
            cursor.execute(totalcount, (session['username'],))
            entry = cursor.fetchone().get('itemnum')
            if (testtotal < 80):
                return redirect(url_for('ineligiblescore'))
            else:
                startpoint = "SELECT `dump{}` FROM `usercounts` WHERE `userid`=%s".format(dump)
                cursor.execute(startpoint, (session['username'],))
                usercount = cursor.fetchone().get('dump{}'.format(dump))
                randomseed = "SELECT `seed` FROM `users` WHERE `userid`=%s"
                cursor.execute(randomseed, (session['username'],))
                seed = cursor.fetchone().get('seed')
                itemlist = "SELECT `Word`, `Filename` FROM `dump{}` ORDER BY RAND({})".format(dump, seed)
                cursor.execute(itemlist)
                query_results = cursor.fetchall()
                total = len(query_results)
                if usercount < total:
                    result = query_results[usercount]
                    word = result.get('Word')
                    filename = result.get('Filename')
                    dumpdisplay = int(dump) - 38  ##CHANGE THIS DEPENDING ON THE DUMP NUMBER YOU ARE AT##
                    filepath = "../static/data/adults/{}".format(filename) ##CHANGE THIS FOR THE DATA YOU NEED##
                    usercount += 1
                    entry += 1
                    return render_template('page.html', filename=filename, word=word, \
                                            filepath=filepath, dumpdisplay=str(dumpdisplay), dump=dump,
                                            usercount=str(usercount), entry=str(entry), total=str(total))
                else:
                    flash("You have completed this set. Thank you!")
                    return redirect(url_for('menu'))
    
@app.route('/results', methods = ['POST', 'GET'])
def results():
    if request.user_agent.platform == 'iphone':
        return redirect(url_for('deny'))
    elif request.method == 'POST':
        word = request.form['word']
        rater = request.form['rater']
        url = request.form['url']
        playtime = request.form['playtime']
        clicktime = request.form['clicktime']
        rating = request.form['rating']
        usercount = request.form['usercount'] 
        entry = request.form['itemnum'] 
        dump = request.form['dump']
        with connection.cursor() as cursor:
            sqlins = "INSERT INTO `ratings` \
                      (word, rater, url, playtime, clicktime, rating) VALUES \
                      (%s, %s, %s, %s, %s, %s)"
            sqluser = "UPDATE `users` \
                       SET `users`.`dumpnum`=%s, `users`.`itemnum`=%s \
                       WHERE `users`.`userid`=%s"
            sqlusercount = "UPDATE `usercounts` \
                            SET `usercounts`.`dump{}`=%s \
                            WHERE `usercounts`.`userid`=%s".format(dump)
            cursor.execute(sqlins, (word, rater, url, playtime, clicktime, rating))
            cursor.execute(sqluser, (dump, entry, rater))
            cursor.execute(sqlusercount, (usercount, rater))
        connection.commit()
        return redirect(url_for('page', dumpnum=dump))
    
@app.route('/demographics')
def demographics():
    return render_template('demographics.html')

@app.route('/ineligible')
def ineligible():
    return redirect(url_for('index'))

@app.route('/welcome', methods = ['POST', 'GET'])
def welcome():
    if request.method == 'POST':
        yearofbirth = request.form['yearofbirth']
        onlyenglish = request.form['onlyenglish']
        englishacquired = request.form['englishacquired']
        englishvariety = request.form['englishvariety']
        englishrhotic = request.form['englishrhotic']
        statereside = request.form['statereside']
        stategrewup = request.form['stategrewup']
        hearingimpairment = request.form['hearingimpairment']
        speechimpairment = request.form['speechimpairment']
        receivedtraining = request.form['receivedtraining']
        receivedtraininglevel = request.form['receivedtraininglevel']
        employed = request.form['employed']
        transcribing = request.form['transcribing']
        hourstranscribing = request.form['hourstranscribing']
        timespentchildren = request.form['timespentchildren']
        headphones = request.form['headphones']
        userid = request.form['userid']
        if (onlyenglish == "1" 
            and hearingimpairment == "0"
            and speechimpairment == "0"):
            with connection.cursor() as cursor:
                sqlins = "INSERT INTO `users` \
                        (yearofbirth, onlyenglish, englishacquired, \
                        englishvariety, englishrhotic, statereside, \
                        stategrewup, hearingimpairment, speechimpairment, \
                        receivedtraining, receivedtraininglevel, employed, \
                        transcribing, hourstranscribing, timespentchildren, \
                        headphones, userid, trainingnum, trainingtotal, itemnum, dumpnum) VALUES \
                        (%s, %s, %s, %s, %s, %s, \
                         %s, %s, %s, %s, %s, %s, \
                         %s, %s, %s, %s, %s, %s, \
                         %s, %s, %s)"
                cursor.execute(sqlins, (yearofbirth, onlyenglish, englishacquired, \
                                        englishvariety, englishrhotic, statereside, \
                                        stategrewup, hearingimpairment, speechimpairment, \
                                        receivedtraining, receivedtraininglevel, employed, \
                                        transcribing, hourstranscribing, timespentchildren, \
                                        headphones, userid, 0, 0, 0, 0))
                itemcountstart = "INSERT INTO `usercounts` (userid) VALUES (%s)"
                cursor.execute(itemcountstart, (userid,))
            flash('User created! Please sign in to continue to the task.') #TODO: check if username exists and requests a new choice
            return redirect(url_for('index'))
        else:
            flash('Unfortunately, you are ineligible to complete this task \
                   based on your responses to the demographic survey.')
            return redirect(url_for('ineligible'))

@app.route('/training')
def training():
    with connection.cursor() as cursor:
        startpoint = "SELECT `trainingnum` FROM `users` WHERE `userid`=%s"
        if cursor.execute(startpoint, (session['username'],)):
            trainingnum = cursor.fetchone().get('trainingnum')
            if trainingnum == 24:
                trainingnum = 0
                sqluser = "UPDATE `users` \
                       SET `users`.`trainingtotal`=%s \
                       WHERE `users`.`userid`=%s"
                cursor.execute(sqluser, (0, session['username']))    
        else:
            trainingnum = 0
        randomseed = "SELECT `seed` FROM `users` WHERE `userid`=%s"
        cursor.execute(randomseed, (session['username'],))
        seed = cursor.fetchone().get('seed')
        itemlist = "SELECT `Word`, `Filename`, `Accuracy` FROM `practice_trials` ORDER BY RAND({})".format(seed)
        cursor.execute(itemlist)
        query_results = cursor.fetchall()
        trainingitemtotal = str(len(query_results))
        result = query_results[trainingnum]
        word = result.get('Word')
        filename = result.get('Filename')
        accuracy = result.get('Accuracy')
        filepath = "../static/data/practice_trials/{}".format(filename)
        pagetype = "Practice"
        action = "/trainresults"
        #global trainingnum
        trainingnum += 1
        instructions = "You must complete this training set before you can proceed to the menu. \
                        Rate each production of /r/ as correct or incorrect. Only rate \
                        productions of /r/ as correct if they sound like an adult-like \
                        production. You will receive feedback after each item."
        return render_template('training.html', filename=filename, word=word, \
                                filepath=filepath, num=str(trainingnum), total=trainingitemtotal, 
                                accuracy=str(accuracy), pagetype=pagetype, action=action, instructions=instructions)
    
@app.route('/trainresults', methods = ['POST', 'GET'])
def trainresults():
    if request.method == 'POST':
        word = request.form['word']
        rater = request.form['rater']
        url = request.form['url']
        playtime = request.form['playtime']
        clicktime = request.form['clicktime']
        rating = request.form['rating']
        accuracy_experts = request.form['cor']
        trainingnum = request.form['num']
        if rating == accuracy_experts:
            accuracy_rater = 1
        else:
            accuracy_rater = 0
        with connection.cursor() as cursor:
            getscore = "SELECT `trainingtotal` FROM `users` WHERE `userid`=%s"
            cursor.execute(getscore, (session['username'],))
            trainingtotal = cursor.fetchone().get('trainingtotal')
            trainingtotal += accuracy_rater
            sqlins = "INSERT INTO `practice_ratings` \
                      (word, rater, url, playtime, clicktime, rating, accuracy_experts, accuracy_rater) VALUES \
                      (%s, %s, %s, %s, %s, %s, %s, %s)"
            sqluser = "UPDATE `users` \
                       SET `users`.`trainingnum`=%s, `users`.`trainingtotal`=%s \
                       WHERE `users`.`userid`=%s"
            cursor.execute(sqlins, (word, rater, url, playtime, clicktime, rating, accuracy_experts, accuracy_rater))
            cursor.execute(sqluser, (trainingnum, trainingtotal, rater))
        connection.commit()
        if int(trainingnum) < 24:
            return redirect(url_for('training'))
        else:
            return redirect(url_for('menu'))
    
@app.route('/test')
def test():
    with connection.cursor() as cursor:
        startpoint = "SELECT `testnum` FROM `users` WHERE `userid`=%s"
        if cursor.execute(startpoint, (session['username'],)):
            testnum = cursor.fetchone().get('testnum')
            if testnum == 100:
                testnum = 0
                sqluser = "UPDATE `users` \
                       SET `users`.`testtotal`=%s \
                       WHERE `users`.`userid`=%s"
                cursor.execute(sqluser, (0, session['username']))
        else:
            testnum = 0
        randomseed = "SELECT `seed` FROM `users` WHERE `userid`=%s"
        cursor.execute(randomseed, (session['username'],))
        seed = cursor.fetchone().get('seed')
        itemlist = "SELECT `Word`, `Filename`, `Accuracy` FROM `test_trials` ORDER BY RAND({})".format(seed)
        cursor.execute(itemlist)
        query_results = cursor.fetchall()
        testitemtotal = 100
        result = query_results[testnum]
        word = result.get('Word')
        filename = result.get('Filename')
        accuracy = result.get('Accuracy')
        filepath = "../static/data/test_trials/{}".format(filename)
        pagetype = "Test Trials"
        action = "/testresults"
        # global testnum
        testnum += 1
        instructions = "You must complete a test set to assess your eligibility for this task. \
                        Rate each production of /r/ as correct or incorrect. Only rate \
                        productions of /r/ as correct if they sound like an adult-like \
                        production. You will NOT receive feedback after each item."
        return render_template('training.html', filename=filename, word=word, \
                                filepath=filepath, num=str(testnum), total=testitemtotal, 
                                accuracy=str(accuracy), pagetype=pagetype, action=action, instructions=instructions)
    
@app.route('/testresults', methods = ['POST', 'GET'])
def testresults():
    if request.method == 'POST':
        word = request.form['word']
        rater = request.form['rater']
        url = request.form['url']
        playtime = request.form['playtime']
        clicktime = request.form['clicktime']
        rating = request.form['rating']
        accuracy_experts = request.form['cor']
        testnum = request.form['num']
        if rating == accuracy_experts:
            accuracy_rater = 1
        else:
            accuracy_rater = 0
        with connection.cursor() as cursor:
            getscore = "SELECT `testtotal` FROM `users` WHERE `userid`=%s"
            cursor.execute(getscore, (session['username'],))
            testtotal = cursor.fetchone().get('testtotal')
            testtotal += accuracy_rater
            sqlins = "INSERT INTO `test_ratings` \
                      (word, rater, url, playtime, clicktime, rating, accuracy_experts, accuracy_rater) VALUES \
                      (%s, %s, %s, %s, %s, %s, %s, %s)"
            sqluser = "UPDATE `users` \
                       SET `users`.`testnum`=%s, `users`.`testtotal`=%s \
                       WHERE `users`.`userid`=%s"
            cursor.execute(sqlins, (word, rater, url, playtime, clicktime, rating, accuracy_experts, accuracy_rater))
            cursor.execute(sqluser, (testnum, testtotal, rater))
        connection.commit()
        if int(testnum) < 100:
            return redirect(url_for('test'))
        elif (int(testnum) == 100) and (int(testtotal) < 80):
            return redirect(url_for('ineligiblescore'))
        else:
            with connection.cursor() as cursor:
                totalcount = "SELECT `itemnum` FROM `users` WHERE `userid`=%s"
                cursor.execute(totalcount, (session['username'],))
                entry = cursor.fetchone().get('itemnum')
                entry += 1
                updateitemnum = "UPDATE `users` \
                                SET `users`.`itemnum`=%s \
                                WHERE `users`.`userid`=%s"
                cursor.execute(updateitemnum, (entry, rater))
                return redirect(url_for('menu'))

# **************************** ADDED RCT PATCH-UP **********************************
@app.route('/rct-menu')            
def rctmenu():
    return render_template('rctmenu.html')

@app.route('/rct-rate/<dumpnum>', methods = ['GET'])
def rctpage(dumpnum):
    dump = dumpnum
    with connection.cursor() as cursor:
        totalcount = "SELECT `itemnum` FROM `users` WHERE `userid`=%s"
        cursor.execute(totalcount, (session['username'],))
        entry = cursor.fetchone().get('itemnum')
        startpoint = "SELECT `dump{}` FROM `usercounts` WHERE `userid`=%s".format(dump)
        cursor.execute(startpoint, (session['username'],))
        usercount = cursor.fetchone().get('dump{}'.format(dump))
        randomseed = "SELECT `seed` FROM `users` WHERE `userid`=%s"
        cursor.execute(randomseed, (session['username'],))
        seed = cursor.fetchone().get('seed')
        itemlist = "SELECT `Word`, `Filename`, `Position` FROM `dump{}` ORDER BY RAND({})".format(dump, seed)
        cursor.execute(itemlist)
        query_results = cursor.fetchall()
        total = len(query_results)
        if usercount < total:
            result = query_results[usercount]
            word = result.get('Word')
            filename = result.get('Filename')
            listed_position = result.get('Position')
            filepath = "../static/data/rct-perception/{}".format(filename) ##CHANGE THIS FOR THE DATA YOU NEED##
            usercount += 1
            entry += 1
            dumpdisplay = int(dump) - 58 ##change this to make it so that the first dump displays as 1##
            position = ''
            if listed_position == 'initial':
                position = 'in initial position'
            elif 'cluster' in listed_position:
                position = 'within a cluster'
            elif 'schwar' in listed_position:
                position = 'following schwa'
            elif listed_position == 'vocalic' or listed_position == 'final':
                position = 'in post-vocalic position'
            else:
                position = 'in initial position'
            return render_template('rctpage.html', filename=filename, word=word, \
                                    filepath=filepath, dump=dump, usercount=str(usercount), \
                                    entry=str(entry), dumpdisplay=str(dumpdisplay), total=str(total), position=position)
        else:
            flash("You have completed this set. Thank you!")
            return redirect(url_for('rctmenu'))
    
@app.route('/rctresults', methods = ['POST', 'GET'])
def rctresults():
    if request.method == 'POST':
        word = request.form['word']
        rater = request.form['rater']
        url = request.form['url']
        playtime = request.form['playtime']
        clicktime = request.form['clicktime']
        rating = request.form['rating']
        usercount = request.form['usercount'] #added 3/14 to deal with global var prob
        entry = request.form['itemnum'] #added 3/14 to deal with global var prob
        dump = request.form['dump'] #added 3/14 to deal with global var prob
        with connection.cursor() as cursor:
            sqlins = "INSERT INTO `rct-perception_ratings` \
                      (word, rater, url, playtime, clicktime, rating) VALUES \
                      (%s, %s, %s, %s, %s, %s)"
            sqluser = "UPDATE `users` \
                       SET `users`.`dumpnum`=%s, `users`.`itemnum`=%s \
                       WHERE `users`.`userid`=%s"
            sqlusercount = "UPDATE `usercounts` \
                            SET `usercounts`.`dump{}`=%s \
                            WHERE `usercounts`.`userid`=%s".format(dump)
            cursor.execute(sqlins, (word, rater, url, playtime, clicktime, rating))
            cursor.execute(sqluser, (dump, entry, rater))
            cursor.execute(sqlusercount, (usercount, rater))
        connection.commit()
        return redirect(url_for('rctpage', dumpnum=dump))    
# ********************************** END RCT PAGES ********************************        
                
                
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['userid']
        study = request.form['study']
        with connection.cursor() as cursor:
            sql = "SELECT `userid` FROM `users`"
            cursor.execute(sql)
            results = [x.get('userid') for x in cursor.fetchall()]
            if user in results:
                session['username'] = user
                session['logged_in'] = True
                if study == 'bcs':
                    return redirect(url_for('menu'))
                elif study == 'rct':
                    return redirect(url_for('rctmenu'))
            else:
                flash('Unknown username.')
                return render_template('login.html')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))
        
if __name__ == '__main__':
    app.run()
