# GDP by County, Metro, and Other Areas | Bureau of Economic Analysis (BEA)

## Instructions for Creating a .zip file for AWS Lambda Deployment
### Follow these steps if you are manually deploying through cloning this project from GitHub

- Prerequisite: Have a recent version of Git, Python and Pip installed on your computer

1. Select (create if needed) a directory where you want to clone this project. Open a terminal window at this desired location.
2. Enter the following command to clone this project:
```
git clone https://github.com/rearc/amazon-data-exchange-bea-gdp-county-metro.git
```
3. Enter the following terminal command to create the .zip file that can be used for AWS Lambda Deployment:
```
rm -r ./pre-processing-code.zip; cd amazon-data-exchange-bea-gdp-county-metro-master/pre-processing/pre-processing-code && pip install numpy pytz pandas --platform manylinux1_x86_64 --no-deps --only-binary=:all: --python-version 37 --abi cp37m --target . && zip -r ../../../pre-processing-code.zip . -x "*.dist-info/*" -x "bin/*" -x "**/__pycache__/*" && rm -r ./*/ && cd ../../..
```
4. A .zip file named ``pre-processing-code.zip`` should now be present in the root directory of your current terminal window that can be used in the AWS Lambda deployment portion of publishing this ADX product.

- If you make adjustments to the files in the ``pre-processing/pre-processing-code/`` directory and need to recreate the ``pre-processing-code.zip`` file, just: 
    1. navigate back to root directory where the current ``pre-processing-code.zip`` is located.
    2. Re-run the terminal command from step 3. Your previous .zip file will be deleted, and a new version will be created containing your adjustments.