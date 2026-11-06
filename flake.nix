{
  description = "Diffable plain-text JSON from *.knxproj files via xknxproject";

  inputs = {
    nullkomma.url = "github:dataheld/nullkomma/eacba26c125e792ff2e2a72339f5da6c55d21fcb";
    nixpkgs.follows = "nullkomma/nixpkgs";
  };

  outputs =
    inputs:
    inputs.nullkomma.lib.mkFlake { inherit inputs; } {
      nullkomma = {
        gitignore = [ ".claude/" ];
        lint.markdown = {
          MD013 = false;
          MD033.allowed-elements = [ "img" ];
        };
        python.enable = true;
        quarto = {
          enable = true;
          brand.enable = true;
        };
        cloudflare = {
          enable = true;
          domain = "maxheld.de";
        };
      };

      partitions.dev = {
        extraInputsFlake = ./dev;
        module =
          { inputs, ... }:
          {
            nullkomma.brand = inputs.brand;
          };
      };

      perSystem =
        { pkgs, ... }:
        {
          process-compose.dev.settings.processes.update-readme = {
            description = "Regenerate the README diff example after test fixtures change";
            disabled = true;
            command = ''
              python -m pytest tests/test_knxray.py::test_git_diff_textconv_snapshot --snapshot-update -q \
                && python scripts/update_readme.py
            '';
          };
          nullkomma.python.test.packages = [ pkgs.git ];
          nullkomma.editor.vscode.settings."files.associations"."*.ambr" = "json";
        };
    };
}
