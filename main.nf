nextflow.enable.dsl=2

params.outdir = "results"

include { FETCH_CARD  } from './modules/fetch_card'
include { RUN_ESMFOLD } from './modules/esmfold'

workflow {
    ch_pathogens = Channel
        .fromPath("data/pathogens.csv")
        .splitCsv(header: true)
        .map { row -> tuple(row.organism, row.gene, row.uniprot_id) }

    FETCH_CARD(ch_pathogens)
    RUN_ESMFOLD(FETCH_CARD.out.fasta)

    RUN_ESMFOLD.out.pdb.view { id, pdb ->
        "Structure ready: ${id} -> ${pdb}"
    }
}
