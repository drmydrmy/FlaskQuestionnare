from flask import Flask
from flask import url_for, render_template, request, redirect, flash
import models

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'the random string'

models.db.app = app
models.db.init_app(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/form')
def form():
    questions = models.Question.query.all()
    return render_template("form.html", questions=questions)


@app.route('/stats')
def stats():
    statistics = list()
    ages = list()
    male_count = 0
    female_count = 0
    kindergarten_count = 0
    underage = 0
    answers_dict = {-2: 'Крайне отрицательное',
                    -1: 'Отрицательное',
                    0: 'Нейтральное',
                    1: 'Положительное',
                    2: 'Крайне положительное'
                    }
    applicants = models.Applicant.query.all()
    questions = models.Question.query.all()
    for i in applicants:
        if i.gender == 'm':
            male_count += 1
        if i.gender == 'f':
            female_count += 1
        if i.education == 'kindergarten':
            kindergarten_count += 1
        if i.age < 18:
            underage += 1
    other_count = len(applicants) - male_count - female_count
    statistics.append(('Всего опрошено', str(len(applicants))))
    for i in applicants:
        ages.append(i.age)
    statistics.append(('Максимальный возраст', str(max(ages))))
    statistics.append(('Минимальный возраст', str(min(ages))))
    statistics.append(('Средний возраст', str(round(sum(ages) / len(ages)))))
    statistics.append(('Мужчин', str(male_count)))
    statistics.append(('Женщин', str(female_count)))
    statistics.append(
        ('С образованием уровня детского сада', str(kindergarten_count)))
    statistics.append(('Несовершеннолетних', str(underage)))
    # Поиск количества всех крайне положительных ответов к каждому вопросу
    # в базе
    for question in questions:
        cur_question_answers = models.db.session.query(models.Answer)\
            .filter(models.Answer.question_id == question.id,
                    models.Answer.answer == 2
                    )
        statistics.append(('Крайне положительно относящихся к ' +
                          question.text[20::],
                          str(cur_question_answers.count())))
    for s in range(3):
        sum_ans = 0
        question = questions[s]
        cur_question_answers = models.db.session.query(models.Answer)\
            .filter(models.Answer.question_id == question.id)
        cur_question_answers = cur_question_answers.all()
        for cur_answer in cur_question_answers:
            sum_ans += cur_answer.answer
        statistics.append(
            ('Среднее отношение к ' + question.text[20::],
             answers_dict[round(sum_ans / len(cur_question_answers))]))
    return render_template("stats.html", statistics=statistics)


@app.route('/process', methods=['get'])
def process():
    if not request.args:
        return redirect(url_for('form'))
    if (request.args.get('age') == '' or
            request.args.get('age', type=int) is None or
            request.args.get('gender') == '' or
            request.args.get('gender') is None):
        if (request.args.get('gender') == '' or
                request.args.get('gender') is None):
            flash('Не указан пол')
        if (request.args.get('age') == '' or
                request.args.get('age', type=int) is None):
            flash('Неверный возраст')
        return redirect(url_for('form'))
    applicant = models.Applicant(
        age=request.args.get('age', type=int),
        gender=request.args.get('gender'),
        education=request.args.get('education'),
        source=request.args.get('source')
    )
    models.db.session.add(applicant)
    models.db.session.commit()
    models.db.session.refresh(applicant)
    questions = models.Question.query.all()
    for question in questions:
        arg_name = 'q' + str(question.id)
        answer = models.Answer(
            applicant_id=applicant.id,
            question_id=question.id,
            answer=request.args.get(arg_name)
        )
        models.db.session.add(answer)
        models.db.session.commit()
    return render_template('thanks.html')


if __name__ == '__main__':
    app.run(debug=True)
