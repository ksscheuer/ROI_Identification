make: AutomaticallyChooseROIs_part1.R
	java -jar ./yesworkflow-0.2.0-jar-with-dependencies.jar graph
	dot -Tpng combined.gv -o cluster_part1.png
	xdg-open cluster_part1.png

clean:
	rm listing.txt combined.gv cluster_part1.png
