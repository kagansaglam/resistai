nextflow.enable.dsl=2

params.outdir = "results"

include { FETCH_CARD     } from './modules/fetch_card'
include { RUN_ESMFOLD    } from './modules/esmfold'
include { FIND_POCKETS   } from './modules/fpocket'
include { SUMMARY_REPORT } from './modules/summary'

workflow {
    ch_pathogens = Channel
        .fromPath("data/pathogens.csv")
        .splitCsv(header: true)
        .map { row -> tuple(row.organism, row.gene, row.uniprot_id) }

    FETCH_CARD(ch_pathogens)
    RUN_ESMFOLD(FETCH_CARD.out.fasta)
    FIND_POCKETS(RUN_ESMFOLD.out.pdb)

    ch_all_jsons = FIND_POCKETS.out.pockets
        .map { id, json -> json }
        .collect()

    SUMMARY_REPORT(ch_all_jsons)

    SUMMARY_REPORT.out.report.view { csv ->
        "Summary report ready: ${csv}"
    }
}
