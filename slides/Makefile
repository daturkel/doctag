MDS := $(wildcard *.md)

slides : $(MDS) 
	@pandoc -f markdown $(MDS) -t beamer --pdf-engine=xelatex --slide-level 2 --highlight-style haddock -o $(basename $(MDS)).pdf
