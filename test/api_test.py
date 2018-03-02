#!/usr/bin/env python

from __future__ import print_function

import requests
import os
import hashlib
import sys

test_server = "http://localhost"
fasta_path = os.path.join( os.path.abspath(__file__), "../test/data-files/")
failures = 0

def get_endpoint(server, request, content_type='text/plain', extra_headers=None):
    r = get(server, request, content_type, extra_headers, die_on_errors=False)

    if r.headers['content-type'] != content_type:
        print("Content-type mismatch, got {}, expected {}".format(r.headers['content-type'],
                                                                  content_type))
        sys.exit(-1)

    if content_type == 'application/json':
        return r.json()
    else:
        return r.text

def get_status_code(server, request, content_type='text/plain', extra_headers=None):
    r = get(server, request, content_type, extra_headers, die_on_errors=False)

    return r.status_code

def get(server, request, content_type='text/plain', extra_headers=None, die_on_errors=True):
    """
    GET an endpoint from the server, allow overriding of default Accept content-type
    """
    header = { "Accept" : content_type }
    if extra_headers:
        header.update(extra_headers)
    r = requests.get(server+request, headers=header)

    if (not r.ok) and die_on_errors:
        r.raise_for_status()
        sys.exit(-1)

    return r

def compare(v1, v2, msg=None):
    global failures

    if v1 == v2:
        return True
    else:
        print("Test: {}, got: {}, expected: {}".format(msg, v1, v2))
        failures += 1
        return False

def test_bulk():
    print( "Testing bulk download of sequences" )

    compare( hashlib.md5(get_endpoint(test_server, "/faidx/2648ae1bacce4ec4b6cf337dcae37816")).hexdigest(), "4f22edfae8576e50c8b1655f4e7312f3", "Bulk download of human chromosome 1 via md5 didn't match expected" )

    compare( hashlib.md5(get_endpoint(test_server, "/faidx/7a822d9b74b1b6c6221bda37bfcdbf426e94f4cf")).hexdigest(), "7bc26323ccba8d6ddcb078711e0b28cc", "Bulk download of cat chromosome A1 via sha1 didn't match expected" )

    compare( hashlib.md5(get_endpoint(test_server, "/faidx/9276c9a0e30e84b5ae5042efe33732aeb48d231ed8ddd6721a2559da251de11f")).hexdigest(), "83b02c391f9109ea4d5106bce5fce846", "Bulk download of cat chromosome A2 via sha256 didn't match expected" )

    compare( hashlib.md5(get_endpoint(test_server, "/faidx/d989dea4a33b3a40683ab2a6bc76c6aa0b957c5f5a982493bef47b4201986ccfa66388456eba09adee859dfd172c7b9f4181dd4d129a54c48a5112d6db50ea91")).hexdigest(), "4f22edfae8576e50c8b1655f4e7312f3", "Bulk download of human chromosome 1 via sha512 didn't match expected" )

    compare( hashlib.md5(get_endpoint(test_server, "/faidx/7a822d9b74b1b6c6221bda37bfcdbf426e94f4cf", content_type='text/x-fasta')).hexdigest(), "2698dc276a70b288700100908bb94c6f", "Bulk download of cat chromosome A1 via sha1 in FASTA didn't match expected" )

#    print hashlib.md5(get_endpoint(test_server, "/faidx/7a822d9b74b1b6c6221bda37bfcdbf426e94f4cf", content_type='application/json')).hexdigest()

#    print get_endpoint(test_server, "/faidx/7a822d9b74b1b6c6221bda37bfcdbf426e94f4cf", content_type='application/json')

def test_querystring():
    print( "Testing start/end paramters" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=0&end=10"), "CCGTACCAGC", "Range starting at 0" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=1&end=10"), "CGTACCAGC", "Testing start=1, end=10" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=10&end=20"), "AGAACCCAAC", "Testing start=10, end=20" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?end=10"), "CCGTACCAGC", "Testing end=10" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=3770&end=3780"), "AATACGTACA", "Testing start=3770, end=3780, end of sequence" )
    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=3770"), "AATACGTACA", "Testing start=3770 to end of sequence" )
    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=3770&end=3779"), "AATACGTAC", "Testing start=3770, end=3779, one back from end of sequence" )
    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=3770&end=3771"), "A", "Testing start=3770, end=3771" )
    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=3779"), "A", "Testing start=3779, one back from end to end of sequence" )

def test_range():
    print( "Testing range query" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "1-10" }), "CCGTACCAGC", "Testing Range 1-10" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "10-10" }), "C", "Testing Ranf 10-10" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "10-11" }), "CA", "Testing Range 10-11" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "3770-3780" }), "AAATACGTACA", "Testing Range 3770-3780, end of sequence" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "3770-3779" }), "AAATACGTAC", "Testing Range 3770-3779" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "3780-3780" }), "A", "Testing Range 3780-3780, last base in sequence" )

def test_metadata():
    print( "Testing metadata endpoint" )

    metadata = {u'metadata': {u'length': 3780, u'id': u'83b02c391f9109ea4d5106bce5fce846', u'aliases': [{u'alias': u'83b02c391f9109ea4d5106bce5fce846'}, {u'alias': u'ae8ed143e88166fa345f39df31050bc69545bf2b'}, {u'alias': u'9276c9a0e30e84b5ae5042efe33732aeb48d231ed8ddd6721a2559da251de11f'}, {u'alias': u'181606c58aa6576ed034afdbc76cae5675d8772084099727a2fadf6f1387038a54f8939599d7ed4f8dce238b4d62c441038bc28692023d6a499c4278c6564317'}, {u'alias': u'A2'}]}}

    compare( get_endpoint(test_server, "/faidx/metadata/83b02c391f9109ea4d5106bce5fce846", content_type='application/json'), metadata, "Testing metadata endpoint" )

def test_multi_range():
    print( "Testing multiple ranges" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", extra_headers={ "Range": "1-10,3770-3780" }), "CCGTACCAGCAAATACGTACA", "Testing Range 1-10,3770-3780" )

def test_strand():
    print( "Testing stand parameter" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?strand=1", extra_headers={ "Range": "3770-3780" }), "AAATACGTACA", "Testing Range 3770-3780, forward strand" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?strand=-1", extra_headers={ "Range": "3770-3780" }), "TGTACGTATTT", "Testing Range 3770-3780, reverse strand" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=0&end=10&strand=-1"), "GCTGGTACGG", "Range starting at 0" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=1&end=10&strand=-1"), "GCTGGTACG", "Testing start=1, end=10" )

def test_errors():
    print( "Testing error codes" )

    compare( get_status_code(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846", content_type='application/json'), 200, "Checking for 200 status" ) 

    compare( get_status_code(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=10&end=10", content_type='application/json'), 400, "Checking for 400 status, invalid start/end" ) 

    compare( get_status_code(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=20&end=10", content_type='application/json'), 400, "Checking for start > end" ) 

    compare( get_status_code(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=10&end=10", content_type='application/json', extra_headers={ "Range": "1-10" }), 400, "Checking for Range and start/end" ) 

    compare( get_status_code(test_server, "/faidx/kwijibo", content_type='application/json'), 404, "Checking for invalid checksum" ) 

def test_translate():
    print( "Testing translating" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?start=554&end=585&translate=1"), "MKYVNQRKTNX", "Testing translating from start/end" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?translate=1", extra_headers={ "Range": "655-686" }), "KCGNKPHESLX", "Testing translating from Range" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?translate=1", extra_headers={ "Range": "554-584,657-686" }), "NEICQSEKDKCVVTNHMSLLX", "Testing multi-range translation" )

    compare( get_endpoint(test_server, "/faidx/83b02c391f9109ea4d5106bce5fce846?translate=1", extra_headers={ "Range": "554-585,666-697" }), "NEICQSEKDKYKPHESLNVREX", "Testing multi-range translate, different frame" )


if __name__ == "__main__":
    """
    Test the REST API
    """

    if len(sys.argv) > 1:
        test_server = sys.argv[1]

    failures = False

    test_bulk()

    test_querystring()

    test_range()

    test_metadata()

    test_multi_range()

    test_strand()

    test_errors()

    test_translate()

    if failures > 0:
        print( "{} tests failed".format(failures) )
        sys.exit(-1)
    else:
        print( "All tests successful" )
        sys.exit(0)
