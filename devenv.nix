{ pkgs, ... }: {
   packages = with pkgs; [ ];
   languages.python.enable = true;
   languages.python.venv.enable = true;
   languages.typescript.enable = true;
}
