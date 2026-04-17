nextflow.enable.dsl=2

params.outdir = "results"

include { FETCH_CARD   } from './modules/fetch_card'
include { RUN_ESMFOLD  } from './modules/esmfold'
include { FIND_POCKETS } from './modules/fpocket'

workflow {
    ch_pathogens = Channel
        .fromPath("data/pathogens.csv")
        .splitCsv(header: true)
        .map { row -> tuple(row.organism, row.gene, row.uniprot_id) }

    FETCH_CARD(ch_pathogens)
    RUN_ESMFOLD(FETCH_CARD.out.fasta)
    FIND_POCKETS(RUN_ESMFOLD.out.pdb)

    FIND_POCKETS.out.pockets.view { id, json ->
        "Pockets ready: ${id} -> ${json}"
    }
}
