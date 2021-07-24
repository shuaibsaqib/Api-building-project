from flask import Flask
from flask_restful import Resource,Api,reqparse,abort,fields,marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)

class TodoModel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    task = db.Column(db.String(200))
    summary = db.Column(db.String(200))

task_post_args = reqparse.RequestParser()
task_post_args.add_argument("task",type=str,help="Task is required",required=True)
task_post_args.add_argument("summary",type=str,help="summary is required",required=True)

task_put_args = reqparse.RequestParser()
task_put_args.add_argument("task",type=str)
task_put_args.add_argument("summary",type=str)

resource_fields ={
    'id' : fields.Integer,
    'task' : fields.String,
    'summary' : fields.String
}

class TodoList(Resource):
    def get(self):
        tasks = TodoModel.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"id" : task.id,  "task" : task.task, "summary" : task.summary}
        return todos    

# db.create_all()


class Todo(Resource):
    @marshal_with(resource_fields)
    def get(self,todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404,message="Could not find the task with this id")
        return task    

    @marshal_with(resource_fields)
    def post(self,todo_id):
        args= task_post_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if task:
            abort(409,message="Task ID already taken")    
        todo = TodoModel(id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(todo)
        db.session.commit()
        return todo,201

    @marshal_with(resource_fields)
    def put(self,todo_id):
        args = task_put_args.parse_args()
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(404,message="Task does not Exist!")
        elif args['task']:
            task.task = args['task']
        elif args['summary']:
            task.summary = args['summary']
        db.session.commit()     
        return task     

    def delete(self,todo_id):
        task = TodoModel.query.filter_by(id=todo_id).first()
        if not task:
            abort(400,message="This id already deleted or does not exist.")
        db.session.delete(task)
        return "successfully deleted",204

api.add_resource(Todo,'/todos/<int:todo_id>')
api.add_resource(TodoList,'/todos')

if __name__ == "__main__":
    app.run(debug=True)
