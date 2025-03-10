import {
    isErrorWithMessage,
    arrayToRecordByKeyName,
    compareSimpleObject,
    getDateAgoSting,
    MINUTE,
    getYesterdayTimeStamp,
    getDateFewDaysAgo,
    getUid,
    mibToBytes,
    formatBytes,
    maskText,
} from './index';

describe('test libs', () => {
    test('Check is error with message', () => {
        expect(isErrorWithMessage({})).toBeFalsy();
        expect(isErrorWithMessage(null)).toBeFalsy();
        expect(isErrorWithMessage({ data: { test: 'test' } })).toBeFalsy();
        expect(isErrorWithMessage({ data: { message: 'error message' } })).toBeTruthy();
    });

    test('array to record by name', () => {
        const mockData = [
            { name: 'test', lastname: 'test_lastname' },
            { name: 'test2', lastname: 'test_lastname2' },
        ];

        expect(arrayToRecordByKeyName(mockData, 'name')).toEqual({
            test: mockData[0],
            test2: mockData[1],
        });

        expect(arrayToRecordByKeyName(mockData, 'lastname')).toEqual({
            test_lastname: mockData[0],
            test_lastname2: mockData[1],
        });
    });

    test('compare simple project', () => {
        expect(compareSimpleObject({ test: 'test' }, { test: 'test' })).toBeTruthy();
        expect(compareSimpleObject({ test: 4 }, { test: 4 })).toBeTruthy();
        expect(compareSimpleObject({ test: 4 }, { test: null })).toBeFalsy();
        expect(compareSimpleObject({ test: undefined }, { test: null })).toBeFalsy();
        expect(compareSimpleObject({ test: 'test', test2: 'test2' }, { test: 'test', test2: 'test2' })).toBeTruthy();
    });

    test('getDateAgoSting', () => {
        const date = new Date();
        const timestamp = date.getTime();
        date.setDate(date.getDate() - 1);
        const day: string = date.getDate() < 10 ? `0${date.getDate()}` : `${date.getDate()}`;
        const month: string = date.getMonth() < 9 ? `0${date.getMonth() + 1}` : `${date.getMonth() + 1}`;
        const year: string = date.getFullYear().toString();

        expect(getDateAgoSting(timestamp)).toEqual('Just now');
        expect(getDateAgoSting(timestamp - MINUTE + 100)).toEqual('Just now');
        expect(getDateAgoSting(timestamp - MINUTE)).toEqual('1 minute ago');
        expect(getDateAgoSting(timestamp - MINUTE * 2)).toEqual('2 minutes ago');
        expect(getDateAgoSting(timestamp - MINUTE * 60)).toEqual('1 hour ago');
        expect(getDateAgoSting(timestamp - MINUTE * 60 * 2)).toEqual('2 hours ago');
        expect(getDateAgoSting(timestamp - MINUTE * 60 * 24)).toEqual(`${day}/${month}/${year}`);
    });

    test('getYesterdayTimeStamp', () => {
        const date = new Date();
        date.setDate(date.getDate() - 1);
        const yesterdayDate = new Date(getYesterdayTimeStamp());

        expect(yesterdayDate.getDate()).toEqual(date.getDate());
        expect(yesterdayDate.getMonth()).toEqual(date.getMonth());
        expect(yesterdayDate.getFullYear()).toEqual(date.getFullYear());
    });

    test('get date few days ago', () => {
        for (let i = 0; i <= 15; i++) {
            const date = new Date();
            const dateAgo = new Date(getDateFewDaysAgo(i));
            date.setDate(date.getDate() - i);

            expect(dateAgo.getDate()).toEqual(date.getDate());
            expect(dateAgo.getMonth()).toEqual(date.getMonth());
            expect(dateAgo.getFullYear()).toEqual(date.getFullYear());
        }

        const date = new Date(1645437591390);
        const dateAgo = new Date(getDateFewDaysAgo(10, date.getTime()));
        date.setDate(date.getDate() - 10);

        expect(dateAgo.getDate()).toEqual(date.getDate());
        expect(dateAgo.getMonth()).toEqual(date.getMonth());
        expect(dateAgo.getFullYear()).toEqual(date.getFullYear());
    });

    test('get unique id', () => {
        const set = new Set();
        const iterationCount = 20;

        for (let i = 0; i < iterationCount; i++) set.add(getUid());

        expect(set.size).toBe(iterationCount);
    });

    test('MiB to Bytes', () => {
        expect(mibToBytes(16384)).toBe(17179869184);
    });

    test('Format bytes', () => {
        expect(formatBytes(0)).toBe('0Bytes');
        expect(formatBytes(1073741824)).toBe('1GB');
        expect(formatBytes(mibToBytes(16384))).toBe('16GB');
    });

    test('Mask text', () => {
        expect(maskText('')).toBe('');
        expect(maskText('test')).toBe('****');
        expect(maskText('test2')).toBe('*****');
    });
});
