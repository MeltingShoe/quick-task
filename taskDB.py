import pickle
import argparse
import readline
import subprocess
import ast
import uuid

'''
takes 0-3 args
if given 0 args it'll enter an interactive mode with menus
if given 1 arg it'll add a new task to ingest with title given in arg
with 2 args it'll also set the body of the new task to the 2nd given arg
with all 3 args it'll categorize the new task instead of adding it to ingest
3rd arg is just a list of descending tasks with the format "['root task', 'subtask', 'sub-subtask']"
if any of the parent tasks are missing they will be created
'''
parser = argparse.ArgumentParser()
parser.add_argument('title', nargs='?')
parser.add_argument('body', nargs='?')
parser.add_argument('parent', nargs='?')
parser.add_argument('--reset', action='store_true', default=False)
args = parser.parse_args()
print(args)


class Task:
    def __init__(self, title, body=''):
        self.title = title
        self.body = body
        self.children = []
        self.priority = False
        self.complete = False

    def addChild(self, task):
        self.children.append(task)

    def chooseChild(self):
        if len(self.children) == 0:
            return self
        print(f"Choosing from <{self.title}>...")
        for count, task in enumerate(self.children):
            print(f"{count + 1}.  <{task.title}>")
        sel = input(f"Select 1-{len(self.children)} or press ENTER to choose <{self.title}> \n")
        if sel == '':
            return self
        if not sel.isdigit():
            print('bad input. try again...')
            return self.chooseChild()
        if int(sel) > len(self.children):
            print('out of range. try again...')
            return self.chooseChild()
        return self.children[int(sel) - 1].chooseChild()

class DB:
    def __init__(self, reset=False):
        if reset:
            self.reset()
        with open('dmp.pkl', 'rb') as f:
            db = pickle.load(f)
        self.tree = db['tree']
        self.ingest = db['ingest']
        print(self.__dict__)

    def reset(self):
        self.tree = Task('root')
        self.ingest = []
        self.save()

    def save(self):
        print('saving...')
        with open('dmp.pkl', 'wb') as f:
            pickle.dump({'tree':self.tree,"ingest":self.ingest}, f)

    def add(self, title=None, body='', parent=None):
        if title == None:
            title = input('enter task name\n')
        task = Task(title, body=body)
        if parent == None:
            self.ingest.append(task)
        else:
            val = taskDB.tree
            path = ast.literal_eval(parent)
            for part in path:
                kids = val.children
                key_exists = False
                for i in kids:
                    if i.title == part:
                        key_exists = True
                        val = i
                if not key_exists:
                    val.children.append(Task(part))
                    val = val.children[-1]
            val.children.append(task)
        taskDB.save()

    def categorize(self):
        if len(taskDB.ingest) == 0:
            return
        task = taskDB.ingest.pop(0)
        print(f"Sorting <{task.title}> ")
        parent = taskDB.tree.chooseChild()

        parent.addChild(task)
        print( f"added <{ task.title }> to <{ parent.title }>..." )
        taskDB.save()

    def view(self):
        task = taskDB.tree.chooseChild()
        print(f"<{task.title}>\n{task.body}")
        return task


def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


if __name__ == '__main__':
    taskDB = DB(args.reset)
    if args.title is None:
        while True:
            sel = input("===|  [t]ree view  |  [a]dd task  |  [c]ategorize  |  [q]uit  |===\n")
            if sel == 'a':
                taskDB.add()
            if sel == 'c':
                taskDB.categorize()
            if sel == 'q':
                break
            if sel == 't':
                task = taskDB.view()
                print(f"===|  SELECTED TASK <{task.title}>  |===")
                print(f"{'=' * 7}|  TASK BODY  |{'=' * 7}\n{task.body}")
                sel = input("------+  [a]dd subtask  +  [e]dit body  +  [q]uit  +------\n")
                if sel == 'q':
                    break
                if sel == 'e':
                    body = subprocess.check_output(['vipe'], input=task.body, text=True)
                    print('edited!')
                    print(body)
                    task.body = body
                    taskDB.save()
                if sel == 'a':
                    title = input(f"Input new task to add to <{task.title}>")
                    body = subprocess.check_output(['vipe']).decode('utf-8')
                    task.addChild(Task(title, body=body))
                    taskDB.save()

        print('exiting...')
        exit()
    taskDB.add(title=args.title, body=args.body, parent=args.parent)
