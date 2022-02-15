from csv import DictReader, reader

def main():
    with open('positions.csv', 'r') as csvf:
        # note  musí byť s čiarkami (",") medzi hodnotami uložené
        csv_dik = DictReader(csvf)
        for row1 in csv_dik:
            print(row1)

if __name__ == '__main__':
    main()