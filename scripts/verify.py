"""Compile and verify using only helper-owned temporary data (JDK 17+, Python 3)."""
from pathlib import Path
import json,os,shutil,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
RESULTS=Path(os.environ.get('TODO_VERIFY_RESULTS_DIR',ROOT/'.verification')).resolve();RESULTS.mkdir(parents=True,exist_ok=True)
def executable(name):
 candidate=Path(os.environ.get('JAVA_HOME',''))/'bin'/(name+'.exe' if os.name=='nt' else name)
 return str(candidate) if candidate.is_file() else shutil.which(name)
java,javac=executable('java'),executable('javac')
if not java or not javac:raise SystemExit('JDK 17+ required; set JAVA_HOME or PATH.')
with tempfile.TemporaryDirectory(prefix='astra-todo-verify-') as owned:
 fixture=Path(owned);classes=fixture/'classes';classes.mkdir()
 sources=sorted([*ROOT.glob('src/**/*.java'),*ROOT.glob('test/**/*.java')])
 subprocess.run([javac,'-encoding','UTF-8','--release','17','-d',str(classes),*[str(p) for p in sources]],check=True,cwd=ROOT)
 unit=subprocess.run([java,'-cp',str(classes),'todo.TaskWorkflowTest',str(fixture/'unit')],capture_output=True,text=True,encoding='utf-8',check=True)
 (RESULTS/'unit.log').write_text(unit.stdout+unit.stderr,encoding='utf-8');result=json.loads(next(x[7:] for x in unit.stdout.splitlines() if x.startswith('RESULT ')));checks=[]
 def cli(name,text,path,expected=0):
  r=subprocess.run([java,'-cp',str(classes),'todo.App',str(path)],input=text,capture_output=True,text=True,encoding='utf-8',timeout=60)
  (RESULTS/(name+'.log')).write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==expected,(name,r.stdout,r.stderr);checks.append(name);return r
 p=fixture/'cli.txt';r=cli('create-eof','1\nCLI task\nSaved description\n',p);assert 'added and saved' in r.stdout and p.exists()
 r=cli('restart-list','2\n5\n',p);assert 'CLI task' in r.stdout
 before=p.read_bytes();cli('cancel-delete','4\n1\nno\n5\n',p);assert p.read_bytes()==before
 r=cli('edit-reopen-search','6\n1\nEdited CLI title\nNew description\n3\n1\n7\n1\n8\nEdited\nopen\n5\n',p);assert 'Edited CLI title' in r.stdout and '[ ] ID 1 / v4' in r.stdout
 before=p.read_bytes();r=cli('incomplete-eof','1\nIncomplete title\n',p);assert p.read_bytes()==before and 'incomplete command' in r.stdout
 r=cli('confirm-delete','4\n1\nDELETE\n5\n',p);assert 'deleted and saved' in r.stdout
 bad=fixture/'bad.txt';bad.write_bytes(b'not a task file');r=cli('corrupt-startup','5\n',bad,1);assert bad.read_bytes()==b'not a task file' and 'existing data was not replaced' in r.stderr
 race=fixture/'race.txt';go=fixture/'go';children=[]
 for i in range(2):
  ready=fixture/('ready'+str(i));child=subprocess.Popen([java,'-cp',str(classes),'todo.TaskWorkflowTest','worker',str(race),str(ready),str(go),'Worker '+str(i)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8');children.append((child,ready))
 try:
  deadline=time.monotonic()+60
  while not all(p.exists() for _,p in children):
   if time.monotonic()>deadline:raise RuntimeError('Worker startup timeout')
   time.sleep(.02)
  go.write_text('go',encoding='utf-8');outputs=[p.communicate(timeout=60) for p,_ in children];assert all(p.returncode==0 for p,_ in children);combined=''.join(out for out,_ in outputs);assert combined.count('ACCEPTED')==1 and combined.count('CONFLICT')==1,outputs
  checks.append('two-jvm-conflict');(RESULTS/'two-jvm.log').write_text(combined,encoding='utf-8')
 finally:
  for child,_ in children:
   if child.poll() is None:child.kill();child.wait()
 evidence={'passed':True,'javaTests':result['tests'],'processChecks':len(checks),'total':result['tests']+len(checks),'checks':checks,'environment':'JDK 17; disposable temporary fixture; no personal task files used'}
 (RESULTS/'results.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8');print(json.dumps(evidence))
