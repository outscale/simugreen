rm -f app1/vscode.zip
rm -f ms1/vscode.zip
rm -f hosts

source env_init.sh
terraform apply --auto-approve

rm -f app1/vscode.zip
rm -f ms1/vscode.zip
rm -f hosts