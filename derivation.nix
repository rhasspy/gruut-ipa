{ lib, nixpkgs ? import <nixpkgs> {}, pythonPkgs ? nixpkgs.pkgs.python38Packages }:
pythonPkgs.buildPythonPackage rec {
  name   = "gruut-ipa-${version}";
  version = "0.10.0";

  src = pythonPkgs.fetchPypi {
    inherit version;
    pname   = "gruut-ipa";
    sha256 = "1kxrpv4qnzqbgv0vprlsvk0y0p58pl9xxz8sm7z4xxbyd1zamicf";
  };

  meta = with lib; {
    homepage    = "https://github.com/rhasspy/gruut-ipa";
    description = "Library for manipulating pronunciations using the International Phonetic Alphabet (IPA)";
    license     = licenses.mit;
    platforms   = platforms.linux;
  };

  doCheck = false;
}
