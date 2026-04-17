process FETCH_CARD {
    publishDir "${params.outdir}/sequences", mode: 'copy'

    input:
    tuple val(organism), val(gene), val(uniprot_id)

    output:
    tuple val(uniprot_id), path("${uniprot_id}.fasta"), emit: fasta

    script:
    """
    python3 ${projectDir}/scripts/fetch_sequences.py \
        "${organism}" "${gene}" "${uniprot_id}"
    """
}
