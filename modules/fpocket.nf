process FIND_POCKETS {
    publishDir "${params.outdir}/pockets", mode: 'copy'

    input:
    tuple val(uniprot_id), path(pdb)

    output:
    tuple val(uniprot_id), path("${uniprot_id}_pockets.json"), emit: pockets

    script:
    """
    python3 ${projectDir}/scripts/find_pockets.py ${uniprot_id} ${pdb}
    """
}
