path_to_function=$1

cd $path_to_function

zip -r9 package.zip lambda_function.py
