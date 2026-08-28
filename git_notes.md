git clone https://github.com/DerellLicht/ndir32

git clone -b dmiller https://daniel.miller@endogiteng01.strykercorp.com/scm/apol/ccu.git dmillerTest
git clone -b dmiller  http://daniel.miller@endoscmeng01.endo.strykercorp.com:7990/scm/apol/ccu.git dmillerTest
 
https://daniel.miller@endogiteng01.strykercorp.com/scm/apol/ccu.git

git clone git@bitbucket.org:vitalconnect/pluto.git -b develop pluto_dev --recursive
   
12/09/2014  What was needed to make this work is:
1. Cannot use https format, must use git/ssh format (for commands)
2. needed to install Cygwin openssh
3. create keys using ssh-keygen
4. need to register public key with bitbucket

12/12/2014  To get Git working on new machine, I copied the .ssh directory from old machine,
then extracted in *both* c:\home\dmiller\.ssh and c:\Users\dmiller\.ssh

//************************************************************************
## Git commands  

- create new branch, local and remote  
git branch new_branch_name  
git checkout new_branch_name  
git push origin new_branch_name:new_branch_name  

- git configuration  
git config --global user.name "Dan Miller"  
git config --global user.email dan7miller@comcast.net  
git config --global credential.helper wincred  

- over-write unwanted changes in local file  
  use "git checkout -- <file>..." to discard changes in working directory

- update existing submodule to match online branch  
git pull

- include submodule in project  
in base project directory, run:  
git submodule add https://github.com/DerellLicht/der_libs

- recover submodule(s), after clone without --recursive  
git submodule update --init --recursive

- delete submodule  
git submodule deinit <path_to_submodule>  
git rm <path_to_submodule>  
git commit -m "Removed submodule "  
rm -rf .git/modules/<path_to_submodule>  

- Initial commit to new remote repository  
[first, create empty repository with this name, on Github ]  
git init .  
git add [as required]  
git commit -m "create repository"  
git remote add origin https://github.com/DerellLicht/derbar  
git push -u origin master  

- fix detached head  
git checkout -b master  
git push --set-upstream origin master  
  
if that doesn't work:  
git reset --hard HEAD^  

- how to make git logs and other reports show date/time in a logical order - forever  
git config --global log.date isov
Thank you, Claude !!  

- log: dump recent commits  
git log -n 10 --oneline  

- log: list all commits on version.h  
git log --follow -p -- version.h  

- dump all commits since last release  
git log --after=11/4/2015 --oneline  

- dump all commits on specific branch  
git log --after=3/13/2015 --oneline branch_name  

- switch to different branch  
git checkout <branch_name>  

- delete branch  
git push origin --delete <remote_branch_name>  

To update existing local repositories about deleted branches:  
git fetch -p  
The -p means prune deleted branches     

- commit/push new files  
git commit -a -m "commit message"  
git push --set-upstream origin branch_name  
git push --all  

To push selected file(s):  
git add filename  
git commit  
git push  

- tagging a commit  
git tag tag_string  

- Deleting a branch  
git push origin --delete <branchName>  

- diff current file with HEAD  
  This *must* be done in root git directory  
  git diff App/src/main.main.c  
  
- rename a branch  
git branch -m <newname>  
git push origin -u <newname>  
git push origin --delete <oldname>    
  
- git merge  
check out target branch (merge-to branch)  
CD to that branch root directory  
git merge origin/ddm_fix_gotos  
git push  

- delete a branch  
To delete the local branch use:  
$ git branch -d branch_name  
or use:  
$ git branch -D branch_name  

As of Git v1.7.0, you can delete a remote branch using  
$ git push origin --delete <branch_name>  

- combine commits and comments  
git rebase -i HEAD~2  
in vi, replace "pick" with "squash" for unwanted items  
git push --force  

This merges last 2 commits into one, with 1 comment  

- Git remote update  

- Git pull := git fetch + git merge  
  git fetch gets info on *only* current branch  
  git pull gets info on *all* branches  
  
- To get remote status:  
  git fetch  
  git status  


