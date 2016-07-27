import json
from flask import Flask
from flask import render_template
from os.path import join, dirname
from watson_developer_cloud import AlchemyLanguageV1
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ubuntu/test.db'
db = SQLAlchemy(app)

alchemy_language = AlchemyLanguageV1(api_key='aa87b3d47dcdc409b05627a6cba65b6184513e06',url="https://access.alchemyapi.com/calls")

class Paragraph(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	content = db.Column(db.String)
	position = db.Column(db.Integer)
	is_analyzed = db.Column(db.Boolean, default = False)
	happiness = db.Column(db.Float)
	sadness = db.Column(db.Float)
	anger = db.Column(db.Float)
	fear = db.Column(db.Float)
	disgust = db.Column(db.Float) 

	def __init__(self, content, position, is_analyzed, happiness, sadness, anger, fear, disgust):
		self.content = content;
		self.position = position
		self.is_analyzed = is_analyzed
		self.happiness = happiness
		self.sadness = sadness
		self.anger = anger
		self.fear = fear
		self.disgust = disgust

	def __repr__(self):
		return self.content

def process_file():
	f = open('frankenstein.txt', 'r')
	data = f.read()
	split_data = data.split("\n\n")
	
	for number, paragraph in enumerate(split_data, 1):
		if paragraph != "":
			p = Paragraph(paragraph, number, False, 0, 0, 0, 0, 0)
			db.session.add(p)
	db.session.commit()

@app.route('/')
def index():
	paragraph = Paragraph.query.all()
	return render_template('index.html', paragraph = paragraph)


@app.route('/update_database')
def update_databse():
	paragraph = Paragraph.query.all()
	for p in paragraph:
		resp_dict = json.loads(json.dumps(alchemy_language.emotion(text=p, language='english')))
		p.anger = int(resp_dict['docEmotions']['anger'])
		p.happiness = int(resp_dict['docEmotions']['joy'])
		p.fear = int(resp_dict['docEmotions']['fear'])
		p.sadness = int(resp_dict['docEmotions']['sadness'])
		p.disgust = int(resp_dict['docEmotions']['disgust'])
		print p.position
	db.session.commit()

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
