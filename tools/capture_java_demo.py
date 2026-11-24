from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
java=Path(r'C:\Program Files\JetBrains\IntelliJ IDEA 2026.2.2\jbr\bin\java.exe')
result=subprocess.run([str(java),'-Dfile.encoding=UTF-8','-Dstdout.encoding=UTF-8','-cp',str(root/'java/target/classes'),
                       'ru.mirea.vrarena.Demo'],capture_output=True,check=True)
text=result.stdout.decode('utf-8').replace('\r\n','\n')
(root/'docs/java_demo_этап3.txt').write_text(text,encoding='utf-8',newline='\n')
print('Exit code:',result.returncode,'lines:',len(text.splitlines()))
