MDS := $(wildcard *.md)

slides : $(MDS) 
	@pandoc $(MDS) -t beamer --pdf-engine=xelatex --slide-level 2 --highlight-style haddock -o $(basename $(MDS)).pdf
