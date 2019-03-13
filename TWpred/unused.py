
    @app.route('/compare', methods=['POST'])
    def compare():
        user1, user2 = request.values['user1'], request.values['user2']
        if user1 == user2:
            return 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            return user1 if prediction else user2


    @app.route('/reload')
    def reload():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB has been RESET', users=[], tweets=[])
    
    @app.route('/testload')
    def testload():
        adduser('NBCNews')
        users = User.query.all()
        tweets = Tweet.query.all()
        return render_template('base.html', title='Home', users=users, tweets=tweets )

