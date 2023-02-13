import csv
import sys


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py data.csv sequence.txt")

    # TODO: Read database file into a variable
    database = []  # здесь будут словари содержащие имя человека и кол-во повторений его генов
    with open(sys.argv[1]) as f:
        reader = csv.DictReader(f)
        for r in reader:
            database.append(r)
    genomes = list(database[0].keys())[1:]  # список всех возможных геномов

    # TODO: Read DNA sequence file into a variable
    with open(sys.argv[2]) as f:
        dnk = f.readline()

    # TODO: Find longest match of each STR in DNA sequence
    count_repetitions_of_genome = {}
    for gene in genomes:
        count_repetitions_of_genome[gene] = longest_match(dnk, gene)
    # TODO: Check database for matching profiles

    name = ""
    for person in database:
        person_true = []
        for gene in genomes:
            person_gene = int(person[gene])
            main_gene = count_repetitions_of_genome[gene]
            if person_gene == main_gene:
                person_true.append(True)
            else:
                person_true.append(False)

        if all(person_true):
            name = person["name"]

    if name:
        print(name)
    else:
        print("No match")
    return


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):

        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:

            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
