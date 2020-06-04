all: sphinx_doc_a/build/latex/sphinx_doc_a.pdf

clean:
	$(MAKE) -C sphinx_doc_a clean
	$(MAKE) -C sphinx_doc_b clean
	rm -rf latex_doc/*.aux
	rm -rf latex_doc/*.pdf

sphinx_doc_b/build/latex/sphinx_doc_b.aux: \
		sphinx_doc_b/source/index.rst \
		sphinx_doc_b/source/conf.py
	$(MAKE) -C sphinx_doc_b latexpdf

latex_doc/latex_doc.aux: latex_doc/latex_doc.tex
	cd latex_doc && pdflatex latex_doc.tex

sphinx_doc_a/build/latex/sphinx_doc_a.pdf: \
		sphinx_doc_a/source/index.rst \
		sphinx_doc_a/source/conf.py \
		sphinx_doc_b/build/latex/sphinx_doc_b.aux \
		latex_doc/latex_doc.aux
	$(MAKE) -C sphinx_doc_a latexpdf
